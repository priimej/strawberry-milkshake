from services.geometry import haversine_distance
from services.graph import Graph

# Assumptions: The Graph class has a 'nodes' attribute which is a dictionary
# mapping node_id to node objects that have 'lat' and 'lng' attributes.
# The Graph actually exists and is properly populated.

def nearest_node(
    graph: Graph,
    lat: float,
    lng: float
) -> int:
    """
    Finds the nearest node in the graph to a given lat/lng.
    Returns the node_id.
    """

    closest_node = None
    min_dist = float("inf")

    for node_id, node in graph.nodes.items():
        dist = haversine_distance(
            lat, lng,
            node.lat, node.lng
        )

        if dist < min_dist:
            min_dist = dist
            closest_node = node_id

    if closest_node is None:
        raise ValueError("Graph has no nodes")

    return closest_node
