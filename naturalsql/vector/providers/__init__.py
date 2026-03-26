"""Embedding providers used by NaturalSQL vector subsystem.

Keep this module lightweight: avoid importing optional providers at import time
so package import does not require optional dependencies.
"""

from naturalsql.vector.providers.base import EmbeddingProvider

__all__ = ["EmbeddingProvider"]
