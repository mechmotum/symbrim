"""Module containing models of the pedals."""
from __future__ import annotations

from abc import abstractmethod
from typing import Any

from sympy import Symbol
from sympy.physics.mechanics import Point, ReferenceFrame, Vector

from brim.core import ModelBase

__all__ = ["PedalsBase"]


class PedalsBase(ModelBase):
    """Base class for the pedals."""

    def define_objects(self) -> None:
        """Define the objects."""
        super().define_objects()
        self._frame = ReferenceFrame(self._add_prefix("frame"))
        self._left_pedal_point = Point(self._add_prefix("LPP"))
        self._right_pedal_point = Point(self._add_prefix("RPP"))
        self._center_point = Point(self._add_prefix("CP"))

    def define_kinematics(self) -> None:
        """Define the kinematics."""
        super().define_kinematics()
        self._left_pedal_point.set_vel(self.frame, 0)
        self._right_pedal_point.set_vel(self.frame, 0)

    @property
    def frame(self) -> ReferenceFrame:
        """Frame of the pedals."""
        return self._frame

    @property
    def center_point(self) -> Point:
        """Center point of the pedals."""
        return self._center_point

    @property
    def left_pedal_point(self) -> Point:
        """Left pedal of the bicycle."""
        return self._left_pedal_point

    @property
    def right_pedal_point(self) -> Point:
        """Right pedal of the bicycle."""
        return self._right_pedal_point

    @property
    @abstractmethod
    def rotation_axis(self) -> Vector:
        """Rotation axis of the pedals."""


class SimplePedals(PedalsBase):
    """Simplified pedal model."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.symbols["radius"]: "Pedal radius.",
            self.symbols["offset"]: "Distance of the pedal point from the center point "
                                    "of the pedals along the rotation axis.",
        }

    @property
    def rotation_axis(self) -> Vector:
        """Rotation axis of the pedals."""
        return self.frame.y

    def define_objects(self) -> None:
        """Define the objects."""
        super().define_objects()
        self.symbols["radius"] = Symbol(self._add_prefix("radius"))
        self.symbols["offset"] = Symbol(self._add_prefix("offset"))

    def define_kinematics(self) -> None:
        """Define the kinematics."""
        super().define_kinematics()
        o, r = self.symbols["offset"], self.symbols["radius"]
        self.left_pedal_point.set_pos(self.center_point,
                                      -o * self.rotation_axis - r * self.frame.x)
        self.right_pedal_point.set_pos(self.center_point,
                                       o * self.rotation_axis + r * self.frame.x)
        self.left_pedal_point.set_vel(self.frame, 0)
        self.right_pedal_point.set_vel(self.frame, 0)
