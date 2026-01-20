# in-house graph representation so we can adjust stuff for skating purposes

#single node just like OSM carrying ID, Lat, and Lng
class Node:
    """
    A single point in the routing graph.
    Usually an intersection or dead-end.
    """

    __slots__ = ("id", "lat", "lng")

    def __init__(self, node_id, lat, lng):
        self.id = node_id
        self.lat = lat
        self.lng = lng


class Graph:
    """
    Lightweight adjacency-list graph optimized for routing.
    """

    def __init__(self):
        # node_id -> Node
        self.nodes = {}

        # node_id -> list of (neighbor_id, weight)
        self.edges = {}

    # --------------------------------------------------
    # Node management
    # --------------------------------------------------

    def add_node(self, node_id, lat, lng):
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(node_id, lat, lng)
            self.edges[node_id] = []

    # --------------------------------------------------
    # Edge management
    # --------------------------------------------------

    def add_edge(self, u, v, weight):
        """
        Add a bidirectional edge between u and v.
        """
        self.edges[u].append((v, weight))
        self.edges[v].append((u, weight))

    # --------------------------------------------------
    # Access helpers
    # --------------------------------------------------

    def neighbors(self, node_id):
        """
        Returns list of (neighbor_id, weight).
        """
        return self.edges.get(node_id, [])

    def edge_weight(self, u, v):
        """
        Get weight between u and v.
        """
        for neighbor, weight in self.edges[u]:
            if neighbor == v:
                return weight
        return float("inf")

    # --------------------------------------------------
    # Debugging / visualization
    # --------------------------------------------------

    def print_summary(self):
        print("Graph Summary")
        print("-------------")
        print(f"Nodes: {len(self.nodes)}")
        print(f"Edges: {sum(len(v) for v in self.edges.values()) // 2}")
        print()

    def print_nodes(self, limit=10):
        print("Nodes:")
        for i, (node_id, node) in enumerate(self.nodes.items()):
            if i >= limit:
                print("  ...")
                break
            print(f"  {node_id}: ({node.lat}, {node.lng})")
        print()

    def print_edges(self, limit=10):
        print("Edges:")
        count = 0
        for u, neighbors in self.edges.items():
            for v, weight in neighbors:
                print(f"  {u} -> {v} (cost={weight:.3f})")
                count += 1
                if count >= limit:
                    print("  ...")
                    return
        print()
        
    def print_node_details(self, node_id):
        if node_id not in self.nodes:
            print(f"Node {node_id} not found")
            return

        node = self.nodes[node_id]
        print(f"Node {node_id}")
        print(f"  Location: ({node.lat}, {node.lng})")
        print("  Neighbors:")

        for neighbor, weight in self.edges[node_id]:
            print(f"    -> {neighbor} (cost={weight:.3f})")

        print()
