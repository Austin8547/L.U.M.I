import os
import time
import threading
import requests
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from src.config import (
    ORS_API_KEY,
    ORS_URL,
    NOMINATIM_SEARCH_URL,
    NOMINATIM_REVERSE_URL,
    OSM_USER_AGENT,
    OSM_DEFAULT_COUNTRY,
    NOMINATIM_RATE_LIMIT_SECONDS,
    NOMINATIM_TIMEOUT,
    GEOCODE_CACHE_SIZE,
    REVERSE_GEOCODE_CACHE_SIZE,
    REVERSE_GEOCODE_ROUND_DIGITS,
    ORS_MAX_ROUTES,
    ORS_CONNECT_TIMEOUT,
    ORS_READ_TIMEOUT,
    ORS_RETRIES,
    ORS_RETRY_SLEEP,
    ORS_DEDUP_DISTANCE_THRESHOLD_M,
    ORS_DEDUP_DURATION_THRESHOLD_S,
    ORS_ALT_TARGET_COUNT,
    ORS_ALT_WEIGHT_FACTOR,
    ORS_ALT_SHARE_FACTOR,
    ROUTE_VARIANTS,
    ORS_MAX_ROADS_IN_DESCRIPTION,
    ORS_WAYPOINT_COUNT,
    ORS_POLYLINE_PRECISION,
)

NOMINATIM_SEARCH = NOMINATIM_SEARCH_URL
NOMINATIM_REVERSE = NOMINATIM_REVERSE_URL
USER_AGENT = OSM_USER_AGENT
MAX_ROUTES = ORS_MAX_ROUTES


_last_nominatim_call = 0.0
_nominatim_lock = threading.Lock()


def _throttle():
    """Nominatim allows ~1 request/second (thread-safe)."""
    global _last_nominatim_call
    with _nominatim_lock:
        wait = NOMINATIM_RATE_LIMIT_SECONDS - (time.time() - _last_nominatim_call)
        if wait > 0:
            time.sleep(wait)
        _last_nominatim_call = time.time()


# ---------------------------------------------------------------- geocoding
@lru_cache(maxsize=GEOCODE_CACHE_SIZE)
def _geocode_cached(place: str, country: str | None):
    _throttle()
    params = {"q": place, "format": "json", "limit": 1}
    if country:
        params["countrycodes"] = country
    r = requests.get(NOMINATIM_SEARCH, params=params,
                     headers={"User-Agent": USER_AGENT}, timeout=NOMINATIM_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if not data:
        return None
    return {
        "name": data[0]["display_name"],
        "lat": float(data[0]["lat"]),
        "lon": float(data[0]["lon"]),
    }


def geocode_place(place: str, country: str | None = OSM_DEFAULT_COUNTRY) -> dict | None:
    """Place name -> {'name', 'lat', 'lon'} or None. Cached; failures are not cached."""
    return _geocode_cached(place.strip().lower(), country)


@lru_cache(maxsize=REVERSE_GEOCODE_CACHE_SIZE)
def _reverse_cached(lat: float, lon: float):
    _throttle()
    params = {"lat": lat, "lon": lon, "format": "json", "zoom": 10}
    r = requests.get(NOMINATIM_REVERSE, params=params,
                     headers={"User-Agent": USER_AGENT}, timeout=NOMINATIM_TIMEOUT)
    r.raise_for_status()
    addr = r.json().get("address", {})
    for field in ("city", "town", "village", "municipality",
                  "suburb", "county", "state_district"):
        if addr.get(field):
            return addr[field]
    return None


def reverse_geocode(lat: float, lon: float) -> str | None:
    """Coordinates -> town name. Rounded to ~1 km so nearby points share a cache entry."""
    try:
        return _reverse_cached(round(lat, REVERSE_GEOCODE_ROUND_DIGITS), round(lon, REVERSE_GEOCODE_ROUND_DIGITS))
    except requests.RequestException:
        return None


# ------------------------------------------------------------------ helpers
def decode_polyline(encoded: str, precision: int = ORS_POLYLINE_PRECISION) -> list[tuple[float, float]]:
    coords, index, lat, lon = [], 0, 0, 0
    factor = 10 ** precision
    while index < len(encoded):
        for is_lat in (True, False):
            shift, result = 0, 0
            while True:
                b = ord(encoded[index]) - 63
                index += 1
                result |= (b & 0x1F) << shift
                shift += 5
                if b < 0x20:
                    break
            delta = ~(result >> 1) if result & 1 else result >> 1
            if is_lat:
                lat += delta
            else:
                lon += delta
        coords.append((lat / factor, lon / factor))
    return coords


def describe_roads(route: dict, max_roads: int = ORS_MAX_ROADS_IN_DESCRIPTION) -> str:
    """Main roads in travel order, e.g. 'NH66, SH66'."""
    totals, order = {}, []
    for seg in route.get("segments", []):
        for step in seg.get("steps", []):
            name = (step.get("name") or "").strip()
            if not name or name == "-":
                continue
            if name not in totals:
                totals[name] = 0
                order.append(name)
            totals[name] += step["distance"]

    if not totals:
        return ""

    main = sorted(totals, key=totals.get, reverse=True)[:max_roads]
    return ", ".join(n for n in order if n in main)


def describe_places(geometry: str, n_points: int = ORS_WAYPOINT_COUNT) -> str:
    """Name towns at evenly spaced points along the route."""
    points = decode_polyline(geometry)
    if len(points) < 3:
        return ""

    places = []
    for k in range(1, n_points + 1):
        lat, lon = points[int(len(points) * k / (n_points + 1))]
        name = reverse_geocode(lat, lon)
        if name and name not in places:
            places.append(name)
    return ", ".join(places)


def _fmt_duration(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    return f"{h}h {m}m" if h else f"{m}m"


# ------------------------------------------------------------------- routing
def _ors_routes(coords: list, alternatives: bool = False,
                extra: dict | None = None, retries: int = ORS_RETRIES):
    """Call ORS with a short timeout and retry. Returns (routes, response_or_None)."""
    body = {"coordinates": coords, "instructions": True, "language": "en"}
    if alternatives:
        body["alternative_routes"] = {
            "target_count": ORS_ALT_TARGET_COUNT,
            "weight_factor": ORS_ALT_WEIGHT_FACTOR,
            "share_factor": ORS_ALT_SHARE_FACTOR,
        }
    if extra:
        body.update(extra)

    last = None
    for attempt in range(retries + 1):
        try:
            r = requests.post(
                ORS_URL, json=body,
                headers={"Authorization": ORS_API_KEY,
                         "Content-Type": "application/json"},
                timeout=(ORS_CONNECT_TIMEOUT, ORS_READ_TIMEOUT),  # (connect, read)
            )
        except requests.RequestException:
            time.sleep(1)
            continue
        last = r
        if r.ok:
            return r.json().get("routes", []), r
        if r.status_code not in (429, 500, 502, 503, 504):
            break  # 4xx: retrying won't help
        time.sleep(ORS_RETRY_SLEEP)
    return [], last


def _is_duplicate(route: dict, kept: list) -> bool:
    d, t = route["summary"]["distance"], route["summary"]["duration"]
    return any(
        abs(k["summary"]["distance"] - d) < ORS_DEDUP_DISTANCE_THRESHOLD_M
        and abs(k["summary"]["duration"] - t) < ORS_DEDUP_DURATION_THRESHOLD_S
        for k in kept
    )


def get_route(start: str, end: str, include_places: bool = True) -> dict:
    """Return up to MAX_ROUTES distinct driving routes between two place names."""
    if not ORS_API_KEY:
        return {"error": "ORS_API_KEY missing. Check your .env file."}

    try:
        s = geocode_place(start)
        e = geocode_place(end)
    except requests.RequestException:
        return {"error": "Geocoding service timed out. Try again shortly."}
    if not s:
        return {"error": f"Could not find place: '{start}'"}
    if not e:
        return {"error": f"Could not find place: '{end}'"}

    coords = [[s["lon"], s["lat"]], [e["lon"], e["lat"]]]

    # Fire all ORS requests at once: wall time = slowest call, not the sum
    jobs = [("alternative", {"alternatives": True})]
    jobs += [(label, {"extra": extra}) for label, extra in ROUTE_VARIANTS]
    with ThreadPoolExecutor(max_workers=len(jobs)) as pool:
        futures = [(label, pool.submit(_ors_routes, coords, **kw))
                   for label, kw in jobs]
        results = [(label, f.result()) for label, f in futures]

    candidates, last_resp = [], None
    for label, (raws, resp) in results:   # job order keeps results deterministic
        if resp is not None:
            last_resp = resp
        for rt in raws:
            if len(candidates) < MAX_ROUTES and not _is_duplicate(rt, candidates):
                rt["_label"] = label
                candidates.append(rt)

    if not candidates:
        if last_resp is None:
            return {"error": "Routing service timed out. Try again shortly."}
        return {"error": f"ORS request failed ({last_resp.status_code}): {last_resp.text}"}

    fastest = min(candidates, key=lambda x: x["summary"]["duration"])
    shortest = min(candidates, key=lambda x: x["summary"]["distance"])

    routes = []
    for rt in sorted(candidates, key=lambda x: x["summary"]["duration"]):
        sm = rt["summary"]
        tags = []
        if rt is fastest:
            tags.append("fastest")
        if rt is shortest:
            tags.append("shortest")
        if not tags:
            tags.append(rt["_label"])

        geometry = rt.get("geometry")
        route = {
            "note": " & ".join(tags),
            "distance_km": round(sm["distance"] / 1000, 1),
            "duration": _fmt_duration(round(sm["duration"] / 60)),
            "via": describe_roads(rt),
        }
        if include_places and geometry:
            route["towns"] = describe_places(geometry)
        routes.append(route)

    return {
        "start": s["name"].split(",")[0],
        "end": e["name"].split(",")[0],
        "routes": routes,
    }