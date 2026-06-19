import networkx as nx
from datetime import datetime,UTC
from itertools import combinations

class GraphBuilder:
    def __init__(self,graph=None):
        if graph is None:
            self.graph=nx.Graph()
        else:
            self.graph = graph
        self.now=datetime.now(UTC).isoformat()

    def create_node(self,concept,candidates,source,trend_id=None):
        if not self.graph.has_node(concept):
            self.graph.add_node(
                concept,
                node_type="entity",
                candidates=candidates,
                resolved=None,
                confidence=0.0,
                mentions=0,
                created_at=self.now,
                last_seen=self.now,
                source_counts={
                    "reddit": 0,
                    "youtube": 0,
                    "google_trends": 0
                },
                trend_ids=set()
            )
        node = self.graph.nodes[concept]
        node["mentions"] += 1
        node["source_counts"][source] += 1
        node["last_seen"] = self.now
        if trend_id:
            node["trend_ids"].add(trend_id)

    def create_all_nodes(self,concepts,source,trend_id=None):
        for concept, candidates in concepts.items():
            self.create_node(
                concept=concept,
                candidates=candidates,
                source=source,
                trend_id=trend_id
            )

    def create_edge(self,concept1: str,concept2: str,source: str):   
        if not self.graph.has_edge(concept1, concept2):
            self.graph.add_edge(
                concept1,
                concept2,
                weight=0,
                created_at=self.now,
                last_seen=self.now,
                source_counts={
                    "reddit": 0,
                    "youtube": 0,
                    "google_trends": 0
                }
            )

        edge = self.graph[concept1][concept2]
        edge["weight"] += 1
        edge["source_counts"][source] += 1
        edge["last_seen"] = self.now

    def create_all_edges(self,concepts: dict,source: str):
        concept_names = list(concepts.keys())
        for concept1, concept2 in combinations(concept_names, 2):
            self.create_edge(
                concept1,
                concept2,
                source
            )

    def add_all_trends(self, data):
        for item in data:
            concepts = item.get("concepts", {})
            if not concepts:
                continue
            source = item["source"]
            trend_id = item["id"]
            self.create_all_nodes(concepts=concepts,source=source,trend_id=trend_id)
            if len(concepts)>1:
                self.create_all_edges(concepts=concepts,source=source)

    def get_node_count(self):
        return self.graph.number_of_nodes()

    def get_edge_count(self):
        return self.graph.number_of_edges()

    def get_neighbors(self, concept):
        if not self.graph.has_node(concept):
            return []
        return list(self.graph.neighbors(concept))
    
    def get_context(self, concept):
        if not self.graph.has_node(concept):
            return ""
        neighbors = self.get_neighbors(concept)
        context = []
        for neighbor in neighbors:
            context.append(neighbor)
            resolved = self.graph.nodes[neighbor]["resolved"]
            if resolved:
                context.append(
                    resolved["description"]
                )
        return " ".join(context)
    
class TagNodeBuilder:
    def __init__(self, graph):
        self.graph = graph
    
    def create_tag_node(self,tag,level):
        tag_node = f"TAG::{tag}"
        if not self.graph.has_node(tag_node):
            self.graph.add_node(
                tag_node,
                node_type="tag",
                tag=tag,
                level=level,
                parent=None,
                children_count=0,
                entity_count=0,
            )
        return tag_node

    def create_hierarchy(self,tag_path):
        created_nodes = []
        for level, tag in enumerate(tag_path):
            node = self.create_tag_node(tag,level)
            created_nodes.append(node)

        for i in range(len(created_nodes)-1,0,-1):
            child = created_nodes[i]
            parent = created_nodes[i - 1]
            edge_exists = self.graph.has_edge(child,parent)
            if not edge_exists:
                self.graph.nodes[child]["parent"] = parent
                self.graph.nodes[parent]["children_count"] += 1
                self.graph.add_edge(
                    child,
                    parent,
                    relation="parent_tag",
                )
            edge = self.graph[child][parent]

        return created_nodes

    def link_entity(self,entity_node,tag_path,confidence):
        tag_nodes = self.create_hierarchy(tag_path)
        deepest_tag = tag_nodes[-1]
        if not self.graph.has_edge(entity_node,deepest_tag):
            self.graph.add_edge(
                entity_node,
                deepest_tag,
                relation="has_tag",
                confidence=confidence,
            )
            for tag_node in tag_nodes:
                self.graph.nodes[tag_node]["entity_count"] += 1
        edge = self.graph[entity_node][deepest_tag]
        edge["confidence"] = max(edge["confidence"],confidence)

    def add_tags(self,entity_node,tags):
        for tag_path, confidence in tags.items():
            self.link_entity(entity_node,list(tag_path),confidence)