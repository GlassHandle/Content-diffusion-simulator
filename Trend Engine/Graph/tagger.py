import pickle
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .config import (TAGGER_MODEL_NAME,TOP_N_TAGS)
from datetime import datetime, UTC, timedelta

class GraphTagger:
    def __init__(self):
        self.model = SentenceTransformer(TAGGER_MODEL_NAME)
        base_dir = Path(__file__).resolve().parent
        self.dataset_dir=(base_dir/"Tags_dataset")
        self.pkl_path = (base_dir.parent.parent/"data" /"dataset"/"tag_embeddings.pkl")
        self.pkl_path.parent.mkdir(parents=True,exist_ok=True)
        self.tag_embeddings = self.load_or_create()

    def prepare_dataset(self):
        tag_paths = []
        tag_texts = []
        tier_columns = ["Tier 1","Tier 2","Tier 3","Tier 4"]

        for file in self.dataset_dir.glob("*.tsv"):
            df = pd.read_csv(file, sep="\t")

            for _, row in df.iterrows():
                path = []
                for col in tier_columns:
                    if col not in df.columns:
                        continue
                    value = str(row[col]).strip()
                    if value and value != "nan":
                        path.append(value)
                if not path:
                    continue
                tag_paths.append(path)
                tag_texts.append(
                    " > ".join(path).lower()
                )

        embeddings = self.model.encode(tag_texts,show_progress_bar=True)
        with open(self.pkl_path, "wb") as f:
            pickle.dump(
                {
                    "paths": tag_paths,
                    "texts": tag_texts,
                    "embeddings": embeddings
                },
                f
            )
        return (tag_paths,tag_texts,embeddings)

    def create_dataset(self):
        embeddings = self.model.encode(self.tags,show_progress_bar=True)
        with open(self.pkl_path, "wb") as f:
            pickle.dump(
                {
                    "tags": self.tags,
                    "embeddings": embeddings
                },
                f
            )

        return embeddings

    def load_or_create(self):
        if self.pkl_path.exists():
            with open(self.pkl_path, "rb") as f:
                data = pickle.load(f)
            self.tag_paths = data["paths"]
            self.tag_texts = data["texts"]
            return data["embeddings"]

        (self.tag_paths,self.tag_texts,embeddings) = self.prepare_dataset()
        return embeddings

    def recently_seen(self, timestamp, hours=2):
        last_seen = datetime.fromisoformat(timestamp)
        return datetime.now(UTC) - last_seen <= timedelta(hours=hours)

    
    def build_neighborhood_context(self,graph, node):
        texts = []
        node_data = graph.nodes[node]
        resolved = node_data.get("resolved")

        if resolved:
            texts.append(resolved.get("label", ""))
            texts.append(resolved.get("description", ""))

        for neighbor in graph.neighbors(node):
            neighbor_resolved = graph.nodes[neighbor].get("resolved")

            if not neighbor_resolved:
                continue

            texts.append(neighbor_resolved.get("label",""))
            texts.append(neighbor_resolved.get("description",""))

        return " ".join(texts)

    def get_tags(self, description, top_n=TOP_N_TAGS, threshold=0.50):
        embedding = self.model.encode(description,show_progress_bar=False)
        scores=cosine_similarity([embedding],self.tag_embeddings)[0]
        tags={}

        for idx in scores.argsort()[::-1]:
            score=float(scores[idx])
            if score < threshold:
                break
            path = tuple(self.tag_paths[idx])
            if path not in tags:
                tags[path] = round(score, 4)
            if len(tags) >= top_n:
                break

        return tags
    
    def get_graph_tags(self,context,top_n=8,threshold=0.50):
        return self.get_tags(
            context,
            top_n=top_n,
            threshold=threshold
        )
    
    def tag_graph(self,graph,tag_builder,hours=2):
        for node,data in list(graph.nodes(data=True)):
            if data.get("node_type") != "entity":
                continue

            if not self.recently_seen(data["last_seen"],hours):
                continue

            resolved = data.get("resolved")
            if not resolved:
                continue

            neighbors = list(graph.neighbors(node))
            if len(neighbors)<2:
                continue
            context = self.build_neighborhood_context(graph,node)

            tags = self.get_graph_tags(context=context)
            if not tags:
                continue
            tag_builder.add_tags(node,tags)

            graph.nodes[node]["tag_context"] = context
            graph.nodes[node]["generated_tags"]=tags