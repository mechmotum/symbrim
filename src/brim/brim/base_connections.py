"""Module containing the base connection classes between the rider and bicycle."""
from __future__ import annotations

from brim.bicycle.cranks import CranksBase
from brim.bicycle.front_frames import FrontFrameBase
from brim.bicycle.rear_frames import RearFrameBase
from brim.core import ConnectionBase, ModelRequirement
from brim.rider.arms import LeftArmBase, RightArmBase
from brim.rider.legs import LeftLegBase, RightLegBase
from brim.rider.pelvis import PelvisBase

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
        ModelRequirement("steer", FrontFrameBase, "Front frame of the bicycle."),
        ModelRequirement("left_arm", LeftArmBase, "Left arm of the rider.", hard=False),
        ModelRequirement("right_arm", RightArmBase, "Right arm of the rider.",
                         hard=False),
    )
    steer: FrontFrameBase
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
