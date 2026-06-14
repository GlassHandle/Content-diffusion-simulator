import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from .config import MODEL_NAME, TYPE_HINTS

class EntityResolver:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)
        self.embedding_cache = {}

    def get_embedding(self, text):
        if text not in self.embedding_cache:
            self.embedding_cache[text] = self.model.encode(text,show_progress_bar=False)
        return self.embedding_cache[text]

    def resolve(self, entity, entity_type, candidates, source_text):
        candidates = [
            candidate
            for candidate in candidates
            if candidate.get("description", "").strip()
        ]
        if not candidates:
            return None

        if len(candidates) == 1:
            return candidates[0]

        context_text = f"Entity: {entity}. Context: {source_text}"
        context_embedding = self.get_embedding(context_text)

        print(f"\n{'=' * 60}")
        print(f"ENTITY: {entity}")
        print(f"TYPE: {entity_type}")
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
        hints = TYPE_HINTS.get(entity_type,[])

        for i, candidate in enumerate(candidates):
            description = candidate["description"].lower()

            if any(hint in description for hint in hints):
                scores[i] += 0.03

            print(
                f'{candidate["label"]}\n'
                f'  Desc  : {candidate["description"]}\n'
                f'  Score : {scores[i]:.4f}\n'
            )

        best_idx = scores.argmax()

        print(f"SELECTED -> {candidates[best_idx]['label']}")
        return candidates[best_idx]

    def resolve_all(self,concepts,entity_candidates,source_text):
        resolved = {}

        for entity, candidates in entity_candidates.items():
            resolved[entity] = self.resolve(
                entity,
                concepts.get(entity, "OTHER"),
                candidates,
                source_text
            )

        return resolved