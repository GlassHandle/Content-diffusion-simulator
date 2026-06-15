"""Main clustering pipeline orchestration."""

import json
from collections import defaultdict, Counter
from typing import List, Dict, Optional, Set
import numpy as np

from .config import (
    INPUT_FILE,
    OUTPUT_FILE,
    EXCLUDED_SOURCES,
    KEYWORD_BLOCKLIST,
    MIN_CONFIDENCE_PROB,
    TOP_TERMS_FOR_LABEL,
)
from .text_builder import build_texts
from .embedder import Embedder
from .clusterer import Clusterer
from .labeler import weighted_label_for_cluster


class ClusteringPipeline:
    """Orchestrates the complete clustering workflow."""

    def __init__(
        self,
        input_file: str = INPUT_FILE,
        output_file: str = OUTPUT_FILE,
        excluded_sources: Optional[Set[str]] = None,
        blocklist: Optional[Set[str]] = None,
        min_confidence_prob: float = MIN_CONFIDENCE_PROB,
        top_terms_for_label: int = TOP_TERMS_FOR_LABEL,
    ):
        """
        Initialize the clustering pipeline.
        """
        self.input_file = input_file
        self.output_file = output_file
        self.excluded_sources = excluded_sources or set(EXCLUDED_SOURCES)
        self.blocklist = blocklist or KEYWORD_BLOCKLIST
        self.min_confidence_prob = min_confidence_prob
        self.top_terms_for_label = top_terms_for_label

        self.embedder = Embedder()
        self.clusterer = Clusterer()
        self.data = []

    def load_data(self) -> None:
        """Load data from input JSON file."""
        with open(self.input_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def build_texts_for_embedding(self) -> tuple[List[str], List[bool]]:
        """
        Build embedding texts and exclusion mask from data.
        """
        embedding_texts = []
        excluded_mask = []

        for item in self.data:
            if item.get("source") in self.excluded_sources:
                excluded_mask.append(True)
                embedding_texts.append("")
            else:
                excluded_mask.append(False)
                e_text, _ = build_texts(
                    item,
                    blocklist=self.blocklist,
                    excluded_sources=self.excluded_sources,
                )
                embedding_texts.append(e_text)

        return embedding_texts, excluded_mask

    def filter_usable_items(
        self,
        embedding_texts: List[str],
        excluded_mask: List[bool],
    ) -> List[int]:
        """
        Get indices of items with usable text.
        """
        return [
            i for i, (excl, text) in enumerate(zip(excluded_mask, embedding_texts))
            if not excl and text.strip()
        ]

    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate semantic embeddings for texts.
        """
        print("Generating semantic embeddings...")
        return self.embedder.encode(texts, show_progress_bar=True)

    def cluster_embeddings(self, embeddings: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """
        Perform UMAP reduction and HDBSCAN clustering.
        """
        print("Reducing dimensions...")
        print("Clustering...")
        return self.clusterer.fit_predict(embeddings)

    def clean_labels(
        self,
        labels: np.ndarray,
        probabilities: np.ndarray,
    ) -> np.ndarray:
        """
        Filter labels by confidence threshold.
        """
        return np.array([
            lab if (lab != -1 and prob >= self.min_confidence_prob) else -1
            for lab, prob in zip(labels, probabilities)
        ])

    def map_to_full_dataset(
        self,
        nonempty_idx: List[int],
        cleaned_labels: np.ndarray,
        excluded_mask: List[bool],
    ) -> np.ndarray:
        """
        Map cluster labels back to the full dataset.
        """
        total_items = len(self.data)
        full_labels = np.full(total_items, -1, dtype=int)

        for idx, lab in zip(nonempty_idx, cleaned_labels):
            full_labels[idx] = int(lab)

        for i, excl in enumerate(excluded_mask):
            if excl:
                full_labels[i] = -1

        return full_labels

    def generate_cluster_labels(self, full_labels: np.ndarray) -> Dict[int, str]:
        """
        Generate human-readable labels for clusters.
        """
        cluster_to_items = defaultdict(list)
        for idx, lab in enumerate(full_labels):
            if lab != -1:
                cluster_to_items[lab].append(self.data[idx])

        cluster_names = {}
        for cid, items in cluster_to_items.items():
            cluster_names[cid] = weighted_label_for_cluster(
                items,
                top_n=self.top_terms_for_label,
                blocklist=self.blocklist,
                excluded_sources=self.excluded_sources,
            )

        return cluster_names

    def attach_cluster_metadata(
        self,
        full_labels: np.ndarray,
        cluster_names: Dict[int, str],
    ) -> None:
        """
        Attach cluster_id and cluster_label to each data item.
        """
        for item, lab in zip(self.data, full_labels):
            item["cluster_id"] = int(lab)
            if lab == -1:
                item["cluster_label"] = "Noise/Unclustered"
            else:
                item["cluster_label"] = cluster_names.get(lab, "Unnamed")

    def generate_summary(self, full_labels: np.ndarray, cluster_names: Dict[int, str]) -> List[Dict]:
        """
        Generate summary statistics for clusters.
        """
        cluster_sizes = Counter(full_labels)
        summary = []
        for cluster_id, size in sorted(
            cluster_sizes.items(),
            key=lambda x: (x[0] == -1, -x[1]),
        ):
            summary.append({
                "cluster_id": int(cluster_id),
                "label": "Noise/Unclustered" if cluster_id == -1 else cluster_names.get(cluster_id, ""),
                "size": int(size),
            })
        return summary

    def write_output(self, full_labels: np.ndarray, cluster_names: Dict[int, str]) -> None:
        """
        Write clustered data and metadata to output JSON file.
        """
        summary = self.generate_summary(full_labels, cluster_names)
        usable_items = sum(1 for lab in full_labels if lab != -1)
        total_items = len(self.data)

        output = {
            "summary": summary,
            "items": self.data,
            "quality": {
                "excluded_sources": list(self.excluded_sources),
                "min_confidence_prob": self.min_confidence_prob,
                "usable_items": usable_items,
                "usable_ratio": round(usable_items / total_items, 4) if total_items else 0,
            },
        }

        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)

    def print_report(self, full_labels: np.ndarray, cluster_names: Dict[int, str]) -> None:
        """
        Print clustering report to console.
        """
        total_items = len(self.data)
        cluster_sizes = Counter(full_labels)
        num_clusters = len([c for c in cluster_sizes if c != -1])
        usable_items = sum(1 for lab in full_labels if lab != -1)
        usable_ratio = usable_items / total_items if total_items else 0

        print(f"\nTotal items: {total_items}")
        print(f"Clusters found: {num_clusters}")
        print(f"Noise/unclustered items: {cluster_sizes.get(-1, 0)}")
        print(f"Usable ratio: {usable_ratio:.2%}")
        print("\nCluster summary:")

        summary = self.generate_summary(full_labels, cluster_names)
        for s in summary:
            print(f"  id={s['cluster_id']:<3} size={s['size']:<4} label={s['label']}")

        print(f"\nWritten to {self.output_file}")

    def run(self) -> None:
        """Execute the complete clustering pipeline."""
        print("Loading data...")
        self.load_data()
        total_items = len(self.data)

        print("Building texts...")
        embedding_texts, excluded_mask = self.build_texts_for_embedding()
        nonempty_idx = self.filter_usable_items(embedding_texts, excluded_mask)

        print(f"Items with usable text (after exclusions): {len(nonempty_idx)} / {total_items}")

        if not nonempty_idx:
            print("No usable text left. Writing everything as noise.")
            for item in self.data:
                item["cluster_id"] = -1
                item["cluster_label"] = "Noise/Unclustered"

            output = {
                "summary": [{"cluster_id": -1, "label": "Noise/Unclustered", "size": total_items}],
                "items": self.data,
                "quality": {
                    "usable_ratio": 0.0,
                    "usable_items": 0,
                },
            }
            with open(self.output_file, "w", encoding="utf-8") as f:
                json.dump(output, f, ensure_ascii=False, indent=4)
            return

        nonempty_embed_texts = [embedding_texts[i] for i in nonempty_idx]

        embeddings = self.generate_embeddings(nonempty_embed_texts)
        labels, probabilities = self.cluster_embeddings(embeddings)
        cleaned_labels = self.clean_labels(labels, probabilities)
        full_labels = self.map_to_full_dataset(nonempty_idx, cleaned_labels, excluded_mask)
        cluster_names = self.generate_cluster_labels(full_labels)

        self.attach_cluster_metadata(full_labels, cluster_names)
        self.write_output(full_labels, cluster_names)
        self.print_report(full_labels, cluster_names)
