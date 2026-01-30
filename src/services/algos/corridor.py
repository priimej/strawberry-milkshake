from collections import deque
from app.services.graph.graph import Graph


def extract_corridor(
    graph: Graph,
    path: list[int],
    depth: int = 3
) -> Graph:
    """
    Extracts a corridor subgraph around a given path.
    Depth = number of edge hops from the path.
    """

    corridor_nodes = set(path)
    queue = deque((node, 0) for node in path)

    # --------------------------------
    # 1️⃣ BFS expansion from path
    # --------------------------------
    while queue:
        node, d = queue.popleft()

        if d >= depth:
            continue

        for neighbor, _ in graph.edges.get(node, []):
            if neighbor not in corridor_nodes:
                corridor_nodes.add(neighbor)
                queue.append((neighbor, d + 1))

    # --------------------------------
    # 2️⃣ Build corridor subgraph
    # --------------------------------
    corridor = Graph()

    for node_id in corridor_nodes:
        node = graph.nodes[node_id]
        corridor.add_node(node_id, node.lat, node.lng)

    for u in corridor_nodes:
        for v, weight in graph.edges.get(u, []):
            if v in corridor_nodes:
                corridor.add_edge(u, v, weight)

    return corridor
