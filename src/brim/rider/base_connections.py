"""Module containing the base connection classes between the rider parts."""
from __future__ import annotations

from brim.core import ConnectionBase, ModelRequirement
from brim.rider.arms import ArmBase, LeftArmBase, RightArmBase
from brim.rider.legs import LeftLegBase, LegBase, RightLegBase
from brim.rider.pelvis import PelvisBase
from brim.rider.torso import TorsoBase

__all__ = ["PelvisToTorsoBase", "ShoulderBase", "LeftShoulderBase", "RightShoulderBase",
           "HipBase", "LeftHipBase", "RightHipBase"]


class PelvisToTorsoBase(ConnectionBase):
    """Base class for the connection between the pelvis and the torso."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("pelvis", PelvisBase, "Pelvis of the rider."),
        ModelRequirement("torso", TorsoBase, "Torso of the rider."),
    )


class ShoulderBase(ConnectionBase):
    """Base class for the shoulder joints."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("torso", TorsoBase, "Torso of the rider."),
        ModelRequirement("arm", ArmBase, "Arm of the rider."),
    )


class LeftShoulderBase(ShoulderBase):
    """Base class for the left shoulder joints."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("arm", LeftArmBase, "Left arm of the rider."),
    )


class RightShoulderBase(ShoulderBase):
    """Base class for the right shoulder joints."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("arm", RightArmBase, "Right arm of the rider."),
    )


class HipBase(ConnectionBase):
    """Base class for the hip joints."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("pelvis", PelvisBase, "Pelvis of the rider."),
        ModelRequirement("leg", LegBase, "Leg of the rider."),
    )
    pelvis: PelvisBase
    leg: LegBase


class LeftHipBase(HipBase):
    """Base class for the left hip joints."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("leg", LeftLegBase, "Leg of the rider."),
    )
    leg: LeftLegBase


class RightHipBase(HipBase):
    """Base class for the right hip joints."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("leg", RightLegBase, "Leg of the rider."),
    )
    leg: RightLegBase
