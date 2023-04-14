"""Module containing the models of the front frame of a bicycle."""
from __future__ import annotations

from abc import abstractmethod
from typing import Any

from sympy import Symbol, symbols
from sympy.physics.mechanics import Point, Vector, inertia

from brim.core import ModelBase, NewtonianBodyMixin, set_default_formulation

__all__ = ["FrontFrameBase", "RigidFrontFrame", "RigidFrontFrameMoore"]


class FrontFrameBase(NewtonianBodyMixin, ModelBase):
    """Base class for the front frame of a bicycle."""

    @property
    @abstractmethod
    def steer_axis(self) -> Vector:
        """Steer axis expressed in the front frame."""

    @property
    @abstractmethod
    def wheel_axis(self) -> Vector:
        """Wheel axis expressed in the front frame."""


@set_default_formulation("moore")
class RigidFrontFrame(FrontFrameBase):
    """Rigid front frame."""

    def define_objects(self):
        """Define the objects of the front frame."""
        super().define_objects()
        self.body.central_inertia = inertia(self.body.frame,
                                            *symbols(self._add_prefix("ixx iyy izz")),
                                            izx=Symbol(self._add_prefix("izx")))
        self._wheel_attachment = Point("wheel_attachment")

    def define_kinematics(self):
        """Define the kinematics of the front frame."""
        super().define_kinematics()
        self.wheel_attachment.set_vel(self.frame, 0)

    @property
    @abstractmethod
    def wheel_axis(self) -> Vector:
        """Wheel axis expressed in the front frame."""

    @property
    def wheel_attachment(self) -> Point:
        """Point representing the attachment of the front wheel."""
        return self._wheel_attachment


class RigidFrontFrameMoore(RigidFrontFrame):
    """Rigid front frame model based on Moore's formulation."""

    formulation: str = "moore"

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the front frame."""
        return {
            **super().descriptions,
            self.symbols["d2"]: "Distance between wheels along the steer axis.",
            self.symbols["d3"]: "Perpendicular distance from the steer axis to the "
                                "center of the front wheel (fork offset).",
            self.symbols["l3"]: "Distance in the front frame x drection from the front "
                                "wheel center to the center of mass of the front "
                                "frame.",
            self.symbols["l4"]: "Distance in the front frame z drection from the front "
                                "wheel center to the center of mass of the front "
                                "frame.",
        }

    def define_objects(self):
        """Define the objects of the front frame."""
        super().define_objects()
        self.symbols.update({
            name: Symbol(self._add_prefix(name)) for name in ("d2", "d3", "l3", "l4")})
        self._steer_attachment = Point("steer_attachment")

    def define_kinematics(self):
        """Define the kinematics of the front frame."""
        super().define_kinematics()
        d2, d3, l3, l4 = (self.symbols[name] for name in ("d2", "d3", "l3", "l4"))
        self.wheel_attachment.set_pos(self.steer_attachment,
                                      d3 * self.body.x + d2 * self.body.z)
        self.body.masscenter.set_pos(self.wheel_attachment,
                                     l3 * self.body.x + l4 * self.body.z)
        self.body.masscenter.set_vel(self.frame, 0)
        self.steer_attachment.set_vel(self.frame, 0)
        self.wheel_attachment.set_vel(self.frame, 0)

    @property
    def steer_axis(self) -> Vector:
        """Steer axis expressed in the front frame."""
        return self.body.z

    @property
    def wheel_axis(self) -> Vector:
        """Wheel axis expressed in the front frame."""
        return self.body.y

    @property
    def steer_attachment(self) -> Point:
        """Attachment point between the rear frame and the front frame.

        Explanation
        -----------
        In Moore's formulation an attachment point between the rear and the front frame
        is defined. This point is defined as the intersection of the steer axis a
        perpendicular line, which passes through the attachment of the rear wheel to the
        rear frame.
        """
        return self._steer_attachment
