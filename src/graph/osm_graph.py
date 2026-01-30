from typing import Tuple
import osmnx as ox
import networkx as nx
import sys

from services.graph.graph import Graph
#from app.services.graph.elevation import elevation_delta
from services.graph.terrain import terrain_penalty
from services.algos.geometry import haversine_distance

# Builds a skating-aware graph for an input city using OSM data.

# Input: city_id (string)
# Output: Graph object with skating costs on edges, a dict of the graph bounds
def build_graph_from_city(input_city: str) -> Tuple[Graph, dict]:

    # --------------------------------------------------
    # Step 1: Download + preprocess OSM data
    # --------------------------------------------------

    G = ox.graph_from_place(
        input_city,
        network_type="walk",
        simplify=True
    )
    
    min_lat = min_lng = float("inf")
    max_lat = max_lng = float("-inf")

    # Undirected because skating is bi-directional
    G = G.to_undirected()

    # --------------------------------------------------
    # Step 2: Create our custom graph
    # --------------------------------------------------

    graph = Graph()

    # --------------------------------------------------
    # Step 3: Add nodes (intersections)
    # --------------------------------------------------

    for node_id, data in G.nodes(data=True):
        graph.add_node( node_id=node_id, lat=data["y"], lng=data["x"])
        min_lat = min(min_lat, data["y"])
        max_lat = max(max_lat, data["y"])
        min_lng = min(min_lng, data["x"])
        max_lng = max(max_lng, data["x"])

    # --------------------------------------------------
    # Step 4: Add edges (road segments)
    # --------------------------------------------------

    # for every edge in the OSM graph
    for u, v, data in G.edges(data=True):

        # ---- Base distance ----
        # compute the haversine distance between the two nodes
        dist_km = haversine_distance(
            graph.nodes[u].lat, graph.nodes[u].lng,
            graph.nodes[v].lat, graph.nodes[v].lng
        )

        # # ---- Elevation penalty ----
        # slope_penalty = elevation_delta(
        #     graph.nodes[u],
        #     graph.nodes[v]
        # )

        # ---- Terrain / surface penalty ----
        surface = data.get("surface")
        highway = data.get("highway")

        terrain_cost = terrain_penalty(surface, highway)

        # ---- Final skating cost ----
        weight = dist_km * terrain_cost

        graph.add_edge(u, v, weight)
           
        bounds = {
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lng": min_lng,
        "max_lng": max_lng
    }

    return graph, bounds

# function for estimating memory usage of a graph. takes in a graph,
# returns memory usage in MB
def estimate_graph_memory(graph: Graph) -> float:
    """
    Rough memory estimate for a graph in MB.
    Good enough for cache eviction decisions.
    """

    size_bytes = 0

    # Nodes
    for node in graph.nodes.values():
        size_bytes += sys.getsizeof(node)
        size_bytes += sys.getsizeof(node.id)
        size_bytes += sys.getsizeof(node.lat)
        size_bytes += sys.getsizeof(node.lng)
        #size_bytes += sys.getsizeof(node.elevation)

    # Edges
    for edge_list in graph.edges.values():
        size_bytes += sys.getsizeof(edge_list)
        for neighbor_id, weight in edge_list:
            size_bytes += sys.getsizeof(neighbor_id)
            size_bytes += sys.getsizeof(weight)

    return size_bytes / (1024 * 1024)

# Wrapper function to load graph from OSM and estimate memory for the manager
# inputs a city_id, returns a tuple of (Graph, bounds dict, memory in MB)
def load_graph_from_osm(city_id: str) -> Tuple[Graph, dict, float]:
    graph, bounds = build_graph_from_city(city_id)
    memory_mb = estimate_graph_memory(graph)
    return graph, bounds, memory_mb