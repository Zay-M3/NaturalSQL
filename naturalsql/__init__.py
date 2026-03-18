"""NaturalSQL - Generate SQL from natural language using DB schema + vector retrieval."""

from naturalsql.api import NaturalSQL
from naturalsql.utils.config import AppConfig

__all__ = [
    "NaturalSQL",
    "AppConfig",
]
