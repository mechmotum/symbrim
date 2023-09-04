"""Module containing the base connection classes between the rider parts."""
from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from brim.core import ConnectionBase, ModelRequirement
from brim.rider.arms import ArmBase, LeftArmBase, RightArmBase
from brim.rider.legs import LeftLegBase, LegBase, RightLegBase
from brim.rider.pelvis import PelvisBase
from brim.rider.torso import TorsoBase

if TYPE_CHECKING:
    with contextlib.suppress(ImportError):
        from brim.utilities.plotting import PlotModel

__all__ = ["SacrumBase", "ShoulderBase", "LeftShoulderBase", "RightShoulderBase",
           "HipBase", "LeftHipBase", "RightHipBase"]


class SacrumBase(ConnectionBase):
    """Base class for the connection between the pelvis and the torso."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("pelvis", PelvisBase, "Pelvis of the rider."),
        ModelRequirement("torso", TorsoBase, "Torso of the rider."),
    )
    pelvis: PelvisBase
    torso: TorsoBase

    def set_plot_objects(self, plot_object: PlotModel) -> None:
        """Set the symmeplot plot objects."""
        super().set_plot_objects(plot_object)
        plot_object.add_line([
            self.pelvis.body.masscenter,
            *(joint.parent_point for joint in self.system.joints),
            self.torso.body.masscenter],
            self.name)


class ShoulderBase(ConnectionBase):
    """Base class for the shoulder joints."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("torso", TorsoBase, "Torso of the rider."),
        ModelRequirement("arm", ArmBase, "Arm of the rider."),
    )
    torso: TorsoBase
    arm: ArmBase


class LeftShoulderBase(ShoulderBase):
    """Base class for the left shoulder joints."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("arm", LeftArmBase, "Left arm of the rider."),
    )
    arm: LeftArmBase


class RightShoulderBase(ShoulderBase):
    """Base class for the right shoulder joints."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("arm", RightArmBase, "Right arm of the rider."),
    )
    arm: RightArmBase


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
