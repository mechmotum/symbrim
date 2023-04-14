from __future__ import annotations

from brim.core.singleton import Singleton

__all__ = ["Registry"]


class Registry(Singleton):
    """Registry to keep track of all existing model and connection types in BRiM."""

    def __init__(self) -> None:
        self._models = set()
        self._connections = set()

    def register_model(self, model: type) -> None:
        """Register a new type in the registry."""
        self._models.add(model)

    def register_connection(self, conn: type) -> None:
        """Register a new type in the registry."""
        self._connections.add(conn)

    @property
    def models(self) -> frozenset[type]:
        """Return the registered models."""
        return frozenset(self._models)

    @property
    def connections(self) -> frozenset[type]:
        """Return the registered connections."""
        return frozenset(self._connections)
