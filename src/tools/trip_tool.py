import time
from langchain_core.tools import tool
from src.osm.route_find import get_route


@tool
def shortest_path(start: str, end: str) -> dict:
    """Find up to 2 driving routes between a starting place and destination.

    Args:
        start: Starting place name, e.g. Trivandrum.
        end: Destination place name, e.g. Kochi.
    """
    t0 = time.perf_counter()
    print(f"[AGENT TOOL] Starting route search from {start} to {end}...")
    
    result = get_route(start, end)
    
    elapsed = time.perf_counter() - t0
    print(f"[AGENT TOOL] Finished in {elapsed:.2f} seconds.")
    return result