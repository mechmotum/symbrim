"""Module containing the base class for bicycles."""
from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from brim.bicycle.front_frames import FrontFrameBase
from brim.bicycle.grounds import GroundBase
from brim.bicycle.pedals import PedalsBase
from brim.bicycle.rear_frames import RearFrameBase
from brim.bicycle.wheels import WheelBase
from brim.core import ModelBase, ModelRequirement

if TYPE_CHECKING:
    from sympy import Symbol

    with contextlib.suppress(ImportError):
        from bicycleparameters import Bicycle

__all__ = ["BicycleBase"]


class BicycleBase(ModelBase):
    """Base class for the bicycles."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("ground", GroundBase, "Submodel of the ground.", False),
        ModelRequirement("rear_frame", RearFrameBase, "Submodel of the rear frame."),
        ModelRequirement("front_frame", FrontFrameBase, "Submodel of the front frame.",
                         False),
        ModelRequirement("rear_wheel", WheelBase, "Submodel of the rear wheel.", False),
        ModelRequirement("front_wheel", WheelBase, "Submodel of the front wheel.",
                         False),
        ModelRequirement("pedals", PedalsBase, "Submodel of the pedals.", False),
    )
    rear_frame: RearFrameBase
    front_frame: FrontFrameBase
    rear_wheel: WheelBase
    front_wheel: WheelBase
    pedals: PedalsBase
    ground: GroundBase

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get a parameters mapping of a model based on a bicycle parameters object."""
        params = super().get_param_values(bicycle_parameters)
        if self.rear_wheel is not None:
            params.update(
                self.rear_wheel.get_param_values(bicycle_parameters, position="rear"))
        if self.front_wheel is not None:
            params.update(
                self.front_wheel.get_param_values(bicycle_parameters, position="front"))
        return params
