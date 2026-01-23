import osmnx as ox
import networkx as nx

from services.graph import Graph
from services.terrain import terrain_penalty
from services.geometry import haversine_distance


# EXPANDED: Get all of Brooklyn instead of just Bath Beach
BROOKLYN_PLACE = "Brooklyn, New York City, New York, USA"

# Or if that's too large, try a bigger neighborhood:
# BROOKLYN_PLACE = "Southwest Brooklyn, Brooklyn, New York City, New York, USA"

# Build the OSM graph for Brooklyn with skating-specific weights
def build_brooklyn_graph() -> Graph:

    # --------------------------------------------------
    # Step 1: Download + preprocess OSM data
    # --------------------------------------------------

    print(f"Downloading OSM data for: {BROOKLYN_PLACE}")
    print("This may take a few minutes for larger areas...")
    
    G = ox.graph_from_place(
        BROOKLYN_PLACE,
        network_type="walk",  # Include pedestrian paths, sidewalks, etc.
        simplify=True
    )

    # Undirected because skating is bi-directional
    G = G.to_undirected()
    
    print(f"Downloaded {len(G.nodes)} nodes and {len(G.edges)} edges")

    # --------------------------------------------------
    # Step 2: Create our custom graph
    # --------------------------------------------------

    graph = Graph()

    # --------------------------------------------------
    # Step 3: Add nodes (intersections)
    # --------------------------------------------------

    for node_id, data in G.nodes(data=True):
        graph.add_node(
            node_id=node_id,
            lat=data["y"],
            lng=data["x"]
        )

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

        # ---- Terrain / surface penalty ----
        surface = data.get("surface")
        highway = data.get("highway")

        terrain_cost = terrain_penalty(surface, highway)

        # ---- Final skating cost ----
        weight = dist_km * terrain_cost

        graph.add_edge(u, v, weight)

    return graph