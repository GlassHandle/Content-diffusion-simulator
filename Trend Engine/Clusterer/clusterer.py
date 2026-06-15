"""Dimensionality reduction and clustering using UMAP and HDBSCAN."""

from typing import Tuple
import numpy as np
import umap
import hdbscan
from .config import (
    UMAP_N_COMPONENTS,
    UMAP_N_NEIGHBORS,
    UMAP_MIN_DIST,
    UMAP_METRIC,
    UMAP_RANDOM_STATE,
    HDBSCAN_MIN_CLUSTER_SIZE,
    HDBSCAN_MIN_SAMPLES,
    HDBSCAN_METRIC,
    HDBSCAN_CLUSTER_SELECTION_METHOD,
    HDBSCAN_CLUSTER_SELECTION_EPSILON,
)


class Clusterer:
    """Performs UMAP dimensionality reduction followed by HDBSCAN clustering."""

    def __init__(
        self,
        umap_n_components: int = UMAP_N_COMPONENTS,
        umap_n_neighbors: int = UMAP_N_NEIGHBORS,
        umap_min_dist: float = UMAP_MIN_DIST,
        umap_metric: str = UMAP_METRIC,
        umap_random_state: int = UMAP_RANDOM_STATE,
        hdbscan_min_cluster_size: int = HDBSCAN_MIN_CLUSTER_SIZE,
        hdbscan_min_samples: int = HDBSCAN_MIN_SAMPLES,
        hdbscan_metric: str = HDBSCAN_METRIC,
        hdbscan_cluster_selection_method: str = HDBSCAN_CLUSTER_SELECTION_METHOD,
        hdbscan_cluster_selection_epsilon: float = HDBSCAN_CLUSTER_SELECTION_EPSILON,
    ):
        self.umap_n_components = umap_n_components
        self.umap_n_neighbors = umap_n_neighbors
        self.umap_min_dist = umap_min_dist
        self.umap_metric = umap_metric
        self.umap_random_state = umap_random_state

        self.hdbscan_min_cluster_size = hdbscan_min_cluster_size
        self.hdbscan_min_samples = hdbscan_min_samples
        self.hdbscan_metric = hdbscan_metric
        self.hdbscan_cluster_selection_method = hdbscan_cluster_selection_method
        self.hdbscan_cluster_selection_epsilon = hdbscan_cluster_selection_epsilon

        self.reducer = None
        self.hdbscan_clusterer = None

    def reduce_dimensions(self, embeddings: np.ndarray) -> np.ndarray:
        """
        Reduce embedding dimensionality using UMAP.
        """
        n_samples = embeddings.shape[0]
        n_neighbors = min(self.umap_n_neighbors, n_samples - 1)

        self.reducer = umap.UMAP(
            n_components=self.umap_n_components,
            n_neighbors=n_neighbors,
            min_dist=self.umap_min_dist,
            metric=self.umap_metric,
            random_state=self.umap_random_state,
        )
        return self.reducer.fit_transform(embeddings)

    def cluster(self, reduced_embeddings: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Cluster using HDBSCAN.
        """
        self.hdbscan_clusterer = hdbscan.HDBSCAN(
            min_cluster_size=self.hdbscan_min_cluster_size,
            min_samples=self.hdbscan_min_samples,
            metric=self.hdbscan_metric,
            cluster_selection_method=self.hdbscan_cluster_selection_method,
            cluster_selection_epsilon=self.hdbscan_cluster_selection_epsilon,
        )
        labels = self.hdbscan_clusterer.fit_predict(reduced_embeddings)
        probabilities = self.hdbscan_clusterer.probabilities_
        return labels, probabilities

    def fit_predict(self, embeddings: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Perform full clustering pipeline: UMAP reduction followed by HDBSCAN.
        """
        reduced = self.reduce_dimensions(embeddings)
        labels, probabilities = self.cluster(reduced)
        return labels, probabilities
