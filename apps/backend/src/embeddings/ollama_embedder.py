"""Ollama-based embedder using nomic-embed-text."""

from typing import List

import ollama


class OllamaEmbedder:
    """Generate embeddings using Ollama with nomic-embed-text."""

    def __init__(self, model: str = "nomic-embed-text"):
        """Initialize embedder.

        Args:
            model: Ollama model name (default: nomic-embed-text)
        """
        self.model = model
        self.dimensions = 768  # nomic-embed-text dimensions

        # Verify Ollama is available
        try:
            ollama.list()
        except Exception as e:
            raise RuntimeError(f"Ollama not available: {e}")

    def embed(self, text: str) -> List[float]:
        """Generate embedding for single text.

        Args:
            text: Text to embed

        Returns:
            List of 768 floats (embedding vector)

        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")

        response = ollama.embeddings(
            model=self.model,
            prompt=text
        )

        return response["embedding"]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        return [self.embed(text) for text in texts]
