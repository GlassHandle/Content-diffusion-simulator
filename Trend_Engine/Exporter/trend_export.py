"""
scores each resolved entity in the graph by mentions x recency x source-spread, 
and aggregates those weights onto the entity's tags. 
"""

from __future__ import annotations
import json
import pickle
from collections import defaultdict
from datetime import datetime, UTC
from .config import (GRAPH_PATH, HALF_LIFE_DAYS, OUT_PATH, TOPICS, OVERRIDES,ROOT_MAP)

def topic_for_path(path) -> str | None:
    path = list(path)
    for nm in reversed(path):          
        if nm in OVERRIDES:
            return OVERRIDES[nm]
    return ROOT_MAP.get(path[0]) if path else None


def topics_for_tags(tag_paths) -> set[str]:
    out: set[str] = set()
    for p in tag_paths:
        t = topic_for_path(p)
        if t:
            out.add(t)
    return out

def entity_tag_paths(graph, node: str) -> list[list[str]]:
    paths: list[list[str]] = []
    for nb in graph.neighbors(node):
        if graph.nodes[nb].get("node_type") != "tag" or graph[node][nb].get("relation") != "has_tag":
            continue
        chain: list[str] = []
        cur = nb
        while cur is not None and graph.has_node(cur) and graph.nodes[cur].get("node_type") == "tag":
            name = graph.nodes[cur].get("tag")
            if name:
                chain.append(name)
            cur = graph.nodes[cur].get("parent")
        if chain:
            paths.append(list(reversed(chain)))  
    return paths

def main() -> None:
    graph = pickle.load(GRAPH_PATH.open("rb"))
    now = datetime.now(UTC)

    seen = [d["last_seen"] for _, d in graph.nodes(data=True)
            if d.get("node_type") == "entity" and d.get("last_seen")]
    newest = datetime.fromisoformat(max(seen)) if seen else None

    tag_weight: dict[str, float] = defaultdict(float)
    topic_weight: dict[str, float] = defaultdict(float)
    entities = []
    for node, d in graph.nodes(data=True):
        if d.get("node_type") != "entity" or not d.get("resolved"):
            continue
        mentions = d.get("mentions", 0)

        try:
            last_seen = datetime.fromisoformat(d["last_seen"])
        except (KeyError, ValueError):
            continue

        age_days = max(0.0, (now - last_seen).total_seconds() / 86400.0)
        recency = 0.5 ** (age_days / HALF_LIFE_DAYS)
        n_sources = sum(1 for v in d.get("source_counts", {}).values() if v > 0)
        weight = mentions * recency * (1.0 + 0.5 * (n_sources - 1))
        if weight <= 0:
            continue

        paths = entity_tag_paths(graph, node)
        if not paths:                 
            continue
        tags = sorted({name for p in paths for name in p})   
        for t in tags:                 
            tag_weight[t] += weight
        for topic in topics_for_tags(paths):  
            topic_weight[topic] += weight
        entities.append({"label": (d["resolved"].get("label") or node), "weight": weight, "tags": tags})

    max_t = max(tag_weight.values()) if tag_weight else 1.0
    tag_trends = {t: round(w / max_t, 3)
                  for t, w in sorted(tag_weight.items(), key=lambda kv: kv[1], reverse=True)}

    max_p = max(topic_weight.values()) if topic_weight else 1.0
    topic_trends = {t: round(topic_weight.get(t, 0.0) / max_p, 3) for t in TOPICS}

    entities.sort(key=lambda e: e["weight"], reverse=True)
    max_e = entities[0]["weight"] if entities else 1.0
    trending_entities = [{"label": e["label"], "weight": round(e["weight"] / max_e, 3), "tags": e["tags"]}
                         for e in entities]

    snapshot = {
        "as_of": now.isoformat(),
        "graph_age_days": round((now - newest).total_seconds() / 86400.0, 1) if newest else None,
        "topic_trends": topic_trends,
        "tag_trends": tag_trends,
        "trending_entities": trending_entities,
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with OUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
    print(f"Wrote {OUT_PATH} | {len(tag_trends)} tags, {len(trending_entities)} entities")


if __name__ == "__main__":
    main()
