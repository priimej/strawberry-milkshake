# app/services/router_engine.py

from services.astar import astar
from services.nearest import nearest_node
from services.geometry import estimate_skate_time_minutes
from services.geometry import path_to_coordinates
from services.geometry import path_distance_km

# --------------------------------------------------
# Internal cached state (PRIVATE)
# --------------------------------------------------

_graph = None

# --------------------------------------------------
# Initialization (called ONCE at startup)
# --------------------------------------------------

def initialize(graph):
    """
    Store the prebuilt OSM graph in memory.
    This should be called exactly once at startup.
    """
    global _graph
    _graph = graph


def _require_graph():
    """
    Safety check to prevent silent failures.
    """
    if _graph is None:
        raise RuntimeError(
            "Router engine not initialized. "
            "Call router_engine.initialize(graph) at startup."
        )
    return _graph


# --------------------------------------------------
# Public routing API (called PER REQUEST)
# --------------------------------------------------

def compute_skate_route(
    start_lat: float,
    start_lng: float,
    end_lat: float,
    end_lng: float,
):
    # graph pulled from startup
    graph = _require_graph()

    # 1️⃣ Snap user points to graph
    start_id = nearest_node(graph, start_lat, start_lng)
    end_id   = nearest_node(graph, end_lat, end_lng)

    if start_id is None or end_id is None:
        return None

    # 2️⃣ Run A*
    path = astar(graph, start_id, end_id)
    if not path:
        return None

    # 3️⃣ Convert path to coordinates
    coordinates = path_to_coordinates(graph, path)

    # 4️⃣ Compute distance from edges
    distance_km = path_distance_km(coordinates)
    # 5️⃣ Skate-time estimate
    skate_time_min = estimate_skate_time_minutes(coordinates, 10)

    return {
        "distance_km": round(distance_km, 2),
        "skate_time_min": skate_time_min,
        "geometry": coordinates
    }
