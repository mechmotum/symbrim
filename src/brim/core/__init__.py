"""Module containing the core elements of BRiM."""

__all__ = ["ModelMeta", "ModelBase", "Requirement", "Connection", "NewtonianBodyMixin"]

from brim.core.mixins import NewtonianBodyMixin
from brim.core.model_base import ModelBase, ModelMeta
from brim.core.requirement import Connection, Requirement
