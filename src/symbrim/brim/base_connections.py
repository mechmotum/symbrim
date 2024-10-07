"""Module containing the base connection classes between the rider and bicycle."""
from __future__ import annotations

from symbrim.bicycle.cranks import CranksBase
from symbrim.bicycle.front_frames import FrontFrameBase
from symbrim.bicycle.rear_frames import RearFrameBase
from symbrim.core import ConnectionBase, ModelRequirement
from symbrim.rider.arms import LeftArmBase, RightArmBase
from symbrim.rider.legs import LeftLegBase, RightLegBase
from symbrim.rider.pelvis import PelvisBase

__all__ = ["HandGripsBase", "PedalsBase", "SeatBase"]


class SeatBase(ConnectionBase):
    """Base class for the connection between the pelvis and the rear frame."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("rear_frame", RearFrameBase, "Rear frame of the bicycle."),
        ModelRequirement("pelvis", PelvisBase, "Pelvis of the rider."),
    )
    rear_frame: RearFrameBase
    pelvis: PelvisBase


class HandGripsBase(ConnectionBase):
    """Base class for the connection between the handlebar and the arms."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("front_frame", FrontFrameBase, "Front frame of the bicycle."),
        ModelRequirement("left_arm", LeftArmBase, "Left arm of the rider.", hard=False),
        ModelRequirement("right_arm", RightArmBase, "Right arm of the rider.",
                         hard=False),
    )
    front_frame: FrontFrameBase
    left_arm: LeftArmBase
    right_arm: RightArmBase


class PedalsBase(ConnectionBase):
    """Base class for the connection between the cranks and the legs."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("left_leg", LeftLegBase, "Left leg of the rider.", hard=False),
        ModelRequirement("right_leg", RightLegBase, "Right leg of the rider.",
                         hard=False),
        ModelRequirement("cranks", CranksBase, "Cranks of the bicycle."),
    )
    left_leg: LeftLegBase
    right_leg: RightLegBase
    cranks: CranksBase
