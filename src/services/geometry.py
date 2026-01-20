import math
import services.graph

#quick function for determining the distance between two points in KM
def haversine_distance(lat1, lon1, lat2, lon2) -> float:
    """
    Returns distance in kilometers between two lat/lng points.
    """
    R = 6371.0  # Earth radius in km

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2)
        * math.sin(d_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

#   
# Converts a list of node_ids into a list of (lat, lng) tuples.
#
def path_to_coordinates(graph, path):


    coordinates = []

    for node_id in path:
        node = graph.nodes[node_id]
        coordinates.append((node.lat, node.lng))

    return coordinates

# 
# Adds up all of the coordinates in a list of coords and then
# returns the total distance in KM.
#
def path_distance_km(coordinates: list) -> float:
    """
    coordinates = [(lat, lng), (lat, lng), ...]
    """

    total = 0.0

    for i in range(len(coordinates) - 1):
        lat1, lng1 = coordinates[i]
        lat2, lng2 = coordinates[i + 1]

        total += haversine_distance(lat1, lng1, lat2, lng2)

    return total

#
# Given an average skate speed and a distance in KM, 
# return the estimated time in minutes.
#
def estimate_skate_time_minutes( coordinates: list, avg_speed_kmh:int ) -> int:
    distance_km = path_distance_km(coordinates)

    hours = distance_km / avg_speed_kmh
    minutes = hours * 60

    return round(minutes, 1)
