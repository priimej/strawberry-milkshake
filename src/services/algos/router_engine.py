# app/services/router_engine.py

from services.algos.astar import astar
from services.algos.nearest import nearest_node
from services.algos.geometry import estimate_skate_time_minutes, path_to_coordinates, path_distance_km
from services.graph.citygraphmanager import CityGraph, CityGraphManager

# --------------------------------------------------
# Internal cached state (PRIVATE)
# This cache stays local to this file exclusively
# --------------------------------------------------

_manager = None

# --------------------------------------------------
# Initialization (called ONCE at startup)
# Takes the input city graph manager and stores it for future use.
# Python passes objects by reference.
# --------------------------------------------------

def initialize(Manager: CityGraphManager):
    """
    Store the prebuilt OSM graph in memory.
    This should be called exactly once at startup.
    """
    global _manager
    _manager = Manager


def _require_manager():
    """
    Safety check to prevent silent failures.
    """
    if _manager is None:
        raise RuntimeError(
            "Router engine not initialized."
            "Call router_engine.initialize(manager) at startup.")
    return _manager


# interact with the city graph manager to get or load city graphs
# loads a city graph from the manager given a city name
# should only loads from landing page, otherwise should be getting from cache
def get_city_graph(city: str):
    # get reference to the same manager in cache
    Manager: CityGraphManager = _require_manager()
    return Manager.get_city(city)

# --------------------------------------------------
# Public routing API (called PER REQUEST)
# --------------------------------------------------

def compute_skate_route(
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
    city: str
):
    # Use the stored cache CityGraphManager to pull the city graphs
    Manager: CityGraphManager = _require_manager()
    # Load the city graph if we have it (WE SHOULD HAVE IT)
    city_graph: CityGraph = Manager.get_city(city)

    # The actual graph we will be working with, without all the wrappers
    graph = city_graph.graph

    # Step 1: Snap user points to graph
    start_id = nearest_node(graph, start_lat, start_lng)
    end_id   = nearest_node(graph, end_lat, end_lng)

    if start_id is None or end_id is None:
        raise ValueError("Start or end point is out of graph bounds.")

    # Step 2: Run A*
    path = astar(graph, start_id, end_id)
    if not path:
        raise ValueError("No path found between start and end points.")

    # Step 3: Convert path to coordinates
    coordinates = path_to_coordinates(graph, path)

    # Step 4: Compute distance from edges
    distance_km = path_distance_km(coordinates)
    # Step 5: Skate-time estimate
    skate_time_min = estimate_skate_time_minutes(coordinates, 10)

    return {
        "distance_km": round(distance_km, 2),
        "skate_time_min": skate_time_min,
        "geometry": coordinates
    }
