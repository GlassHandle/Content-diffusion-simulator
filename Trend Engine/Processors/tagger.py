import pickle
import pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .config import MODEL_NAME

class Tagger:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
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

    def get_tags(self, description, top_n=8, threshold=0.55):
        embedding = self.model.encode(description,show_progress_bar=False)
        scores=cosine_similarity([embedding],self.tag_embeddings)[0]
        tags={}

        for idx in scores.argsort()[::-1]:
            score=float(scores[idx])
            if score < threshold:
                break
            path=" > ".join(self.tag_paths[idx])
            if path not in tags:
                tags[path] = round(score, 4)
            if len(tags) >= top_n:
                break

        return tags
