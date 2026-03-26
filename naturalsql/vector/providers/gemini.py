from typing import List
from naturalsql.vector.providers.base import EmbeddingProvider
from google import genai
from google.genai import types

class GeminiEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using Google's Gemini API."""

    def __init__(self, api_key: str, model: str = "models/text-embedding-004"):
        if not api_key:
            raise ValueError("Gemini API Key is required for Gemini provider.")
        try:
            self.client = genai.Client(api_key=api_key)
        except Exception as e:
            raise ValueError(f"Failed to configure Gemini API: {e}")
        self.model = model

    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Embed a list of documents using Gemini API."""
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=documents,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
            )
            return [embedding.values for embedding in response.embeddings]
        except Exception as e:
            raise RuntimeError(f"Failed to embed document with Gemini: {e}")

    def embed_query(self, query: str) -> List[float]:
        """Embed a single query string using Gemini API."""
        try:
            response = self.client.models.embed_content(
                model=self.model,
                contents=query,
                config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
            )
            return response.embeddings[0].values
        except Exception as e:
            raise RuntimeError(f"Failed to embed query with Gemini: {e}")
