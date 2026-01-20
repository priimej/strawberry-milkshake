import heapq
from services.geometry import haversine_distance

def heuristic(graph, a, b):
    na = graph.nodes[a]
    nb = graph.nodes[b]

    return haversine_distance(
        na.lat, na.lng,
        nb.lat, nb.lng
    )

def reconstruct_path(came_from, current):
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    path.reverse()
    return path


def astar(graph, start_id, goal_id):
    open_set = []
    heapq.heappush(open_set, (0, start_id))

    came_from = {}

    g_score = {start_id: 0.0}
    f_score = { start_id: heuristic(graph, start_id, goal_id) }

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal_id:
            return reconstruct_path(came_from, current)

        for neighbor, weight in graph.neighbors(current):
            tentative_g = g_score[current] + weight

            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score[neighbor] = tentative_g + heuristic(
                    graph, neighbor, goal_id
                )
                heapq.heappush(
                    open_set, (f_score[neighbor], neighbor)
                )

    return None
