"""Module containing the core elements of SymBRiM."""

__all__ = [
    "Attachment", "Hub",
    "Singleton",
    "Registry",
    "ConnectionRequirement", "ModelRequirement",
    "ConnectionMeta", "LoadGroupMeta", "ModelMeta",
    "ConnectionBase", "LoadGroupBase", "ModelBase",
    "set_default_convention",
    "NewtonianBodyMixin",
    "AuxiliaryDataHandler", "AuxiliaryData",
]

from symbrim.core.attachment import Attachment, Hub
from symbrim.core.auxiliary import AuxiliaryData, AuxiliaryDataHandler
from symbrim.core.base_classes import (
    ConnectionBase,
    ConnectionMeta,
    LoadGroupBase,
    LoadGroupMeta,
    ModelBase,
    ModelMeta,
    set_default_convention,
)
from symbrim.core.mixins import NewtonianBodyMixin
from symbrim.core.registry import Registry
from symbrim.core.requirement import ConnectionRequirement, ModelRequirement
from symbrim.core.singleton import Singleton
