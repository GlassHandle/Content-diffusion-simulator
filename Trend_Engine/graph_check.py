from pathlib import Path
from Graph import GraphStore

store = GraphStore()
graph = store.load()

base_dir = Path(__file__).resolve().parent
analysis_dir = (base_dir.parent/"data"/"analysis")
analysis_dir.mkdir(parents=True,exist_ok=True)

resolved = []
unresolved = []
tags = []
entities = []

for node, data in graph.nodes(data=True):
    node_type = data.get("node_type")
    if node_type == "entity":
        entities.append(
            (node,data.get("mentions", 0),len(list(graph.neighbors(node)))))
        if data.get("resolved"):
            resolved.append(
                (
                    node,
                    data["resolved"].get("label", ""),
                    data["resolved"].get("description", ""),
                    data.get("confidence", 0.0)
                )
            )
        else:
            unresolved.append(node)

    elif node_type == "tag":
        tags.append(
            (
                node,
                data.get("entity_count", 0),
                data.get("children_count", 0)
            )
        )


with open(analysis_dir / "graph_summary.txt","w",encoding="utf-8") as f:
    f.write(f"Nodes: {graph.number_of_nodes()}\n")
    f.write(f"Edges: {graph.number_of_edges()}\n")
    f.write(f"Resolved Entities: {len(resolved)}\n")
    f.write(f"Unresolved Entities: {len(unresolved)}\n")
    f.write(f"Tag Nodes: {len(tags)}\n")

with open(analysis_dir / "resolved_entities.txt","w",encoding="utf-8") as f:
    for node, label, description, confidence in sorted(resolved):
        f.write(
            f"{node}\n"
            f"  label      : {label}\n"
            f"  description: {description}\n"
            f"  confidence : {confidence:.4f}\n\n"
        )

with open(analysis_dir / "unresolved_entities.txt","w",encoding="utf-8") as f:
    for node in sorted(unresolved):
        f.write(f"{node}\n")

with open(analysis_dir / "tags.txt","w",encoding="utf-8") as f:
    for tag, entity_count, children_count in sorted(tags):
        f.write(
            f"{tag}\n"
            f"  entity_count  : {entity_count}\n"
            f"  children_count: {children_count}\n\n"
        )

entities.sort(key=lambda x: x[1],reverse=True)

with open(analysis_dir / "top_entities.txt","w",encoding="utf-8") as f:
    for node, mentions, degree in entities[:100]:
        f.write(
            f"{node}\n"
            f"  mentions : {mentions}\n"
            f"  neighbors: {degree}\n\n"
        )

print("Analysis files written successfully.")