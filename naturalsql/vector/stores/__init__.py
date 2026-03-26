"""Vector stores used by NaturalSQL vector subsystem.

Keep this module lightweight: avoid importing optional stores at import time
so package import does not require optional dependencies.
"""

from naturalsql.vector.stores.base import VectorStore

__all__ = ["VectorStore"]
