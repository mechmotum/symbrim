"""Module containing pelvis models."""
from __future__ import annotations

from typing import Any

from sympy import Symbol
from sympy.physics.mechanics import Point

from brim.core import ModelBase, NewtonianBodyMixin

__all__ = ["PelvisBase", "SimpleRigidPelvis"]


class PelvisBase(NewtonianBodyMixin, ModelBase):
    """Base class for the pelvis of a rider."""

    @property
    def left_hip_point(self) -> Point:
        """Location of the left hip.

        Explanation
        -----------
        The left hip point is defined as the point where the left hip joint is located.
        This point is used by connections to connect the left leg to the pelvis.
        """
        return self._left_hip_point

    @property
    def right_hip_point(self) -> Point:
        """Location of the right hip.

        Explanation
        -----------
        The right hip point is defined as the point where the right hip joint is
        located. This point is used by connections to connect the right leg to the
        pelvis.
        """
        return self._right_hip_point

    def define_objects(self) -> None:
        """Define the objects."""
        super().define_objects()
        self._left_hip_point = Point(self._add_prefix("LHP"))
        self._right_hip_point = Point(self._add_prefix("RHP"))


class SimpleRigidPelvis(PelvisBase):
    """A simple rigid pelvis.

    Explanation
    -----------
    The simple rigid pelvis models the pelvis as being a rigid body. The hip joints are
    located a hip width apart from each other with the center of mass at the center.
    """

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.symbols["hip_width"]: "Distance between the left and right hip"
                                       "points.",
        }

    def define_objects(self) -> None:
        """Define the objects."""
        super().define_objects()
        self.symbols["hip_width"] = Symbol(self._add_prefix("hip_width"))

    def define_kinematics(self) -> None:
        """Define the kinematics."""
        super().define_kinematics()
        self.left_hip_point.set_pos(self.body.masscenter,
                                    -self.symbols["hip_width"] * self.y / 2)
        self.right_hip_point.set_pos(self.body.masscenter,
                                     self.symbols["hip_width"] * self.y / 2)
