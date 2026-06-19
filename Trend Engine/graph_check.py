from Graph import GraphStore

store = GraphStore()

graph = store.load()

print(f"Nodes: {graph.number_of_nodes()}")
print(f"Edges: {graph.number_of_edges()}")

resolved = 0
unresolved = 0

for node, data in graph.nodes(data=True):
    if data.get("node_type") != "entity":
        continue
    
    if graph.nodes[node]["resolved"]:
        print(f"{node}:{graph.nodes[node]["resolved"]["description"]}")
    else:
        print(f"{node}:None")
    if data.get("resolved") is not None:
        resolved += 1
    else:
        unresolved += 1

print(f"Resolved Entities: {resolved}")
print(f"Unresolved Entities: {unresolved}")