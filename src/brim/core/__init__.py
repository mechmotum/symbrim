"""Module containing the core elements of BRiM."""

__all__ = [
    "ModelMeta", "ModelBase", "traverse_submodels",
    "Requirement", "Connection",
    "NewtonianBodyMixin"
]

from brim.core.mixins import NewtonianBodyMixin
from brim.core.model_base import ModelBase, ModelMeta, traverse_submodels
from brim.core.requirement import Connection, Requirement
