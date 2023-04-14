"""Module containing the core elements of BRiM."""

__all__ = [
    "Singleton",
    "Registry",
    "ConnectionRequirement", "ModelRequirement",
    "ConnectionMeta", "ModelMeta",
    "ConnectionBase", "ModelBase",
    "set_default_formulation",
    "NewtonianBodyMixin",
]

from brim.core.mixins import NewtonianBodyMixin
from brim.core.model_base import (
    ConnectionBase,
    ConnectionMeta,
    ModelBase,
    ModelMeta,
    set_default_formulation,
)
from brim.core.registry import Registry
from brim.core.requirement import ConnectionRequirement, ModelRequirement
from brim.core.singleton import Singleton
