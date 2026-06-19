from datetime import datetime, UTC
from .config import MAX_AGE_DAYS

class GraphPruner:
    def __init__(self, graph):
        self.graph = graph

    def age_in_days(self, timestamp):
        last_seen = datetime.fromisoformat(timestamp)
        return (datetime.now(UTC) - last_seen).days

    def prune_tag(self, tag_node):
        current = tag_node
        while current is not None:
            if not self.graph.has_node(current):
                break
            data = self.graph.nodes[current]
            if data.get("node_type") != "tag":
                break

            if (data["entity_count"] > 0 or data["children_count"] > 0):
                break

            parent = data["parent"]
            self.graph.remove_node(current)
            if (parent is not None and self.graph.has_node(parent)):
                self.graph.nodes[parent]["children_count"] -= 1

            current = parent

    def prune_entities(self):
        nodes_to_remove = []
        for node, data in self.graph.nodes(data=True):
            if data.get("node_type") != "entity":
                continue
            age = self.age_in_days(data["last_seen"])
            if age > MAX_AGE_DAYS:
                nodes_to_remove.append(node)

        for entity_node in nodes_to_remove:
            tag_neighbors = []
            for neighbor in self.graph.neighbors(entity_node):
                edge = self.graph[entity_node][neighbor]
                if edge.get("relation") == "has_tag":
                    tag_neighbors.append(neighbor)

            for tag_node in tag_neighbors:
                if not self.graph.has_node(tag_node):
                    continue

                current = tag_node
                while (current is not None and self.graph.has_node(current)):
                    self.graph.nodes[current]["entity_count"] -= 1
                    current = self.graph.nodes[current]["parent"]

            self.graph.remove_node(entity_node)

            for tag_node in tag_neighbors:
                self.prune_tag(tag_node)

    def prune_edges(self):
        edges_to_remove = []
        for u, v, data in self.graph.edges(data=True):
            relation = data.get("relation")
            if relation in {"parent_tag","has_tag"}:
                continue
            if "last_seen" not in data:
                continue
            age = self.age_in_days(data["last_seen"])
            if age > MAX_AGE_DAYS:
                edges_to_remove.append((u, v))

        self.graph.remove_edges_from(edges_to_remove)


    def prune_graph(self):
        self.prune_entities()
        self.prune_edges()