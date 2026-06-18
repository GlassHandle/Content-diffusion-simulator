import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .config import MODEL_NAME

class EntityResolver:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.embedding_cache = {}

    def get_embedding(self, text):
        if text not in self.embedding_cache:
            self.embedding_cache[text] = self.model.encode(text,show_progress_bar=False)
        return self.embedding_cache[text]

    def resolve(self, entity, candidates, source_text, DEBUG=False):
        candidates = [
            candidate
            for candidate in candidates
            if candidate.get("description", "").strip()
        ]
        if not candidates:
            return None

        if len(candidates) == 1:
            candidate = candidates[0]
            if not candidate.get("description"):
                return None

            return candidate

        context_text = f"Entity: {entity}. Context: {source_text}"
        context_embedding = self.get_embedding(context_text)

        if DEBUG:
            print(f"\n{'=' * 60}")
            print(f"ENTITY: {entity}")
            print(f"{'=' * 60}")

        candidate_texts = [f'{candidate["label"]} {candidate["description"]}' for candidate in candidates]

        uncached = [
            text
            for text in candidate_texts
            if text not in self.embedding_cache
        ]

        if uncached:
            embeddings = self.model.encode(uncached,show_progress_bar=False)
            for text, embedding in zip(uncached,embeddings):
                self.embedding_cache[text] = embedding

        candidate_matrix = np.array([self.embedding_cache[text] for text in candidate_texts])
        scores = cosine_similarity([context_embedding],candidate_matrix)[0]
        best_idx = scores.argmax()

        if DEBUG:
            print(f"SELECTED -> {candidates[best_idx]}")
        return candidates[best_idx]

    def resolve_all(self,entity_candidates,source_text):
        resolved = {}

        for entity, candidates in entity_candidates.items():
            resolved[entity] = self.resolve(
                entity,
                candidates,
                source_text
            )

        return resolved