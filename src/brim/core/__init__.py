"""Module containing the core elements of BRiM."""

__all__ = [
    "Singleton",
    "Requirement",
    "ConnectionMeta", "ModelMeta",
    "ConnectionBase", "ModelBase",
    "NewtonianBodyMixin",
]

from brim.core.mixins import NewtonianBodyMixin
from brim.core.model_base import ConnectionBase, ConnectionMeta, ModelBase, ModelMeta
from brim.core.requirement import Requirement
from brim.core.singleton import Singleton
