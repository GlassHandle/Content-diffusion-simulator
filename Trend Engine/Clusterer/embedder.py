"""Semantic embedding generation using SentenceTransformer."""

from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer
from .config import EMBEDDING_MODEL


class Embedder:
    """Encapsulates SentenceTransformer model for semantic embeddings."""

    def __init__(self, model_name: str = EMBEDDING_MODEL):
        """
        Initialize embedder with a SentenceTransformer model.

        Args:
            model_name: Name of the SentenceTransformer model to load.
        """
        self.model_name = model_name
        self.model: SentenceTransformer = None

    def load(self) -> None:
        """Load the SentenceTransformer model."""
        if self.model is None:
            self.model = SentenceTransformer(self.model_name)

    def encode(
        self,
        texts: List[str],
        show_progress_bar: bool = True,
    ) -> np.ndarray:
        """
        Encode a list of texts into semantic embeddings.

        Args:
            texts: List of text strings to embed.
            show_progress_bar: Whether to show a progress bar.

        Returns:
            Array of shape (len(texts), embedding_dim).
        """
        if self.model is None:
            self.load()
        return self.model.encode(texts, show_progress_bar=show_progress_bar)

    def get_embedding_dimension(self) -> int:
        """
        Get the dimensionality of embeddings from this model.

        Returns:
            Embedding dimension size.
        """
        if self.model is None:
            self.load()
        return self.model.get_sentence_embedding_dimension()
