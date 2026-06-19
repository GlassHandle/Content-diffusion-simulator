from pathlib import Path
from Graph.graph_builder import GraphBuilder,TagNodeBuilder
from Graph.entity_resolver import GraphEntityResolver
from Graph.tagger import GraphTagger
import json

BASE_DIR = Path(__file__).resolve().parent
SOURCES = {"reddit", "youtube", "google-trends"}

curr_dir = BASE_DIR.parent / "data" / "temp"

graph = GraphBuilder()

complete_data = []

for source in SOURCES:
    with open(curr_dir / f"{source}.json","r",encoding="utf-8") as f:
        data = json.load(f)
    complete_data.extend(data)

graph.add_all_trends(complete_data)

entity_resolver = GraphEntityResolver(graph.graph)

entity_resolver.resolve_all()

tagger = GraphTagger()
tag_builder = TagNodeBuilder(graph.graph)
tagger.tag_graph(graph.graph,tag_builder)

debug_path = (BASE_DIR.parent/ "data"/ "temp"/ "graph_debug.txt")

with open(
    debug_path,
    "w",
    encoding="utf-8"
) as f:

    f.write("=" * 80 + "\n")
    f.write("ENTITY NODES\n")
    f.write("=" * 80 + "\n")

    for node, data in graph.graph.nodes(data=True):

        if str(node).startswith("TAG::"):
            continue

        resolved = data.get("resolved")

        f.write(f"\nNODE: {node}\n")

        if resolved:

            f.write(
                f"Resolved: "
                f"{resolved.get('label')} | "
                f"{resolved.get('description')}\n"
            )

        f.write(
            f"Tags: "
            f"{data.get('generated_tags', {})}\n"
        )

        f.write(
            f"Context: "
            f"{data.get('tag_context', '')}\n"
        )

    f.write("\n\n")
    f.write("=" * 80 + "\n")
    f.write("TAG NODES\n")
    f.write("=" * 80 + "\n")

    for node, data in graph.graph.nodes(data=True):

        if not str(node).startswith("TAG::"):
            continue

        f.write(f"\n{node}\n")

        f.write(
            f"Level: "
            f"{data.get('level')}\n"
        )

    f.write("\n\n")
    f.write("=" * 80 + "\n")
    f.write("TAG HIERARCHY\n")
    f.write("=" * 80 + "\n")

    for u, v, edge_data in graph.graph.edges(data=True):

        if (
            str(u).startswith("TAG::")
            and
            str(v).startswith("TAG::")
        ):

            f.write(
                f"{u} --> {v}\n"
            )

    f.write("\n\n")
    f.write("=" * 80 + "\n")
    f.write("ENTITY -> TAG\n")
    f.write("=" * 80 + "\n")

    for u, v, edge_data in graph.graph.edges(data=True):

        if (
            edge_data.get("relation")
            ==
            "has_tag"
        ):

            f.write(
                f"{u} --> {v}\n"
            )

print(
    f"Debug written to: "
    f"{debug_path}"
)

