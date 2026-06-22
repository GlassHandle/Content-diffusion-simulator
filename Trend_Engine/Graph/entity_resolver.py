import numpy as np
from sentence_transformers import SentenceTransformer
from .config import (SIM_THRESHOLD,ENTITY_RESOLVER_MODEL_NAME)

class GraphEntityResolver:
    def __init__(self,graph,model_name=ENTITY_RESOLVER_MODEL_NAME):
        self.graph = graph
        self.model = SentenceTransformer(model_name)
        self.embedding_cache = {}
        self._precompute_candidate_embeddings()

    def candidate_text(self, candidate):
        return (f"{candidate.get('label', '')}. "f"{candidate.get('description', '')}").strip()

    def get_embedding(self, text):
        text = (text or "").strip().lower()
        if text not in self.embedding_cache:
            emb = self.model.encode(text,convert_to_numpy=True,show_progress_bar=False)

            norm = np.linalg.norm(emb)
            if norm > 0:
                emb = emb / norm

            self.embedding_cache[text] = emb
        return self.embedding_cache[text]

    def _precompute_candidate_embeddings(self):
        for node,data in self.graph.nodes(data=True):
            if data.get("node_type") != "entity":
                continue

            if data.get("resolved") is not None:
                continue

            node_data = self.graph.nodes[node]
            candidates = node_data.get("candidates", [])

            embs_list = []
            for candidate in candidates:
                emb = self.get_embedding(self.candidate_text(candidate))
                candidate["_emb"] = emb
                embs_list.append(emb)

            if embs_list:
                node_data["_candidate_matrix"] = np.array(embs_list)
            else:
                node_data["_candidate_matrix"] = None

    def candidate_prior(self, rank):
        return 1.0 / (rank + 1)
    
    def coherence_score(self,node,candidate_emb):
        score = 0.0
        contributing_neighbors = 0

        for neighbor in self.graph.neighbors(node):
            edge_weight = self.graph[node][neighbor].get("weight", 1)
            neighbor_matrix = self.graph.nodes[neighbor].get("_candidate_matrix")

            if neighbor_matrix is None or len(neighbor_matrix) == 0:
                continue

            similarities = neighbor_matrix @ candidate_emb
            best_similarity = similarities.max()

            if best_similarity > SIM_THRESHOLD:
                score += edge_weight * float(best_similarity)
                contributing_neighbors += 1

        if contributing_neighbors == 0:
            return 0.0

        return score / contributing_neighbors

    def resolve_node(self, node):
        node_data = self.graph.nodes[node]
        candidates = node_data.get("candidates", [])

        if not candidates:
            return None

        neighbors = list(self.graph.neighbors(node))
        best_candidate = None
        best_score = -float("inf")
        debug_scores = {}

        prior_weight = max(0.1,0.3 - (0.02 * len(neighbors)))
        coherence_weight = 1.0 - prior_weight

        for rank, candidate in enumerate(candidates):
            candidate_emb = candidate["_emb"]
            prior_score = self.candidate_prior(rank)
            coherence_score = self.coherence_score(node, candidate_emb)

            final_score = (prior_weight * prior_score + coherence_weight * coherence_score)

            debug_scores[candidate.get("id")] = {
                "label": candidate.get("label"),
                "description": candidate.get("description", ""),
                "prior": float(prior_score),
                "coherence": float(coherence_score),
                "final": float(final_score)
            }

            if final_score > best_score:
                best_score = final_score
                best_candidate = candidate

        node_data["resolved"] = best_candidate
        node_data["confidence"] = float(best_score)
        node_data["resolution_debug"] = debug_scores

        return best_candidate

    def resolve_all(self):
        resolved_count = 0
        for node,data in self.graph.nodes(data=True):
            if data.get("node_type") != "entity":
                continue
            if data.get("resolved") is not None:
                continue
            candidates = data.get("candidates", [])

            if not candidates:
                continue

            if len(candidates)==1:
                data["resolved"] = candidates[0]
                data["confidence"] = 1.0
                resolved_count += 1
                continue

            neighbors = list(self.graph.neighbors(node))

            if len(neighbors) < 2:
                continue

            result = self.resolve_node(node)
            if result is not None:
                resolved_count += 1
        return resolved_count