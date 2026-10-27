import time
from src.osm.route_find import get_route


def test_get_route():
    # Start the timer
    start_time = time.perf_counter()
    
    out = get_route("Trivandrum", "Kochi")
    
    # End the timer
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    if "error" in out:
        print(f"Error: {out['error']}")
        print(f"Time taken: {elapsed_time:.2f} seconds")
        return

    print(f"{out['start']} -> {out['end']}")
    print(f"Execution time: {elapsed_time:.2f} seconds\n")

    for route in out["routes"]:
        print(
            f"Route {route['route_index']} ({route['note']}): "
            f"{route['distance_km']} km, "
            f"~{route['duration_min']} min"
        )
        print(f"    {route['via']}")

        if route["places"]:
            print(f"    {route['places']}")

        print()


if __name__ == "__main__":
    test_get_route()