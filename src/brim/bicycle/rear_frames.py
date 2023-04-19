"""Module containing the models of the rear frame of a bicycle."""
from __future__ import annotations

from abc import abstractmethod
from typing import Any

from sympy import Symbol, symbols
from sympy.physics.mechanics import Point, Vector, inertia

from brim.core import ModelBase, NewtonianBodyMixin, set_default_formulation

__all__ = ["RearFrameBase", "RigidRearFrame", "RigidRearFrameMoore"]


class RearFrameBase(NewtonianBodyMixin, ModelBase):
    """Base class for the rear frame of a bicycle."""

    @property
    @abstractmethod
    def steer_axis(self) -> Vector:
        """Steer axis expressed in the rear frame."""

    @property
    @abstractmethod
    def wheel_axis(self) -> Vector:
        """Wheel axis expressed in the rear frame."""

    @property
    @abstractmethod
    def saddle(self) -> Point:
        """Point representing the saddle."""


@set_default_formulation("moore")
class RigidRearFrame(RearFrameBase):
    """Rigid rear frame."""

    def define_objects(self):
        """Define the objects of the rear frame."""
        super().define_objects()
        self.body.central_inertia = inertia(self.body.frame,
                                            *symbols(self._add_prefix("ixx iyy izz")),
                                            izx=Symbol(self._add_prefix("izx")))
        self._wheel_attachment = Point(self._add_prefix("wheel_attachment"))
        self._saddle = Point(self._add_prefix("saddle"))

    def define_kinematics(self):
        """Define the kinematics of the rear frame."""
        super().define_kinematics()
        self.wheel_attachment.set_vel(self.frame, 0)
        self.saddle.set_vel(self.frame, 0)

    def define_loads(self):
        """Define the loads acting upon the rear frame."""
        super().define_loads()

    @property
    @abstractmethod
    def steer_axis(self) -> Vector:
        """Steer axis expressed in the rear frame."""

    @property
    def wheel_axis(self) -> Vector:
        """Wheel axis expressed in the rear frame."""
        return self.body.y

    @property
    def wheel_attachment(self) -> Point:
        """Point representing attachment of the rear wheel."""
        return self._wheel_attachment

    @property
    def saddle(self) -> Point:
        """Point representing the saddle."""
        return self._saddle


class RigidRearFrameMoore(RigidRearFrame):
    """Rigid rear frame model based on Moore's formulation."""

    formulation: str = "moore"

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the rear frame."""
        return {
            **super().descriptions,
            self.symbols["d1"]: "Perpendicular distance from the steer axis to the "
                                "center of the rear wheel (rear offset).",
            self.symbols["l1"]: "Distance in the rear frame x drection from the rear "
                                "wheel center to the center of mass of the rear frame.",
            self.symbols["l2"]: "Distance in the rear frame z drection from the rear "
                                "wheel center to the center of mass of the rear frame.",
            self.symbols["d4"]: "Distance in the rear frame x drection from the rear "
                                "wheel center to the point representing the saddle.",
            self.symbols["d5"]: "Distance in the rear frame z drection from the rear "
                                "wheel center to the point representng the saddle.",
        }

    def define_objects(self):
        """Define the objects of the rear frame."""
        super().define_objects()
        self.symbols.update({
            name: Symbol(self._add_prefix(name)) for name in ("d1", "l1", "l2", "d4",
                                                              "d5")})
        self._steer_attachment = Point("steer_attachment")

    def define_kinematics(self):
        """Define the kinematics of the rear frame."""
        super().define_kinematics()
        d1, l1, l2, d4, d5 = (self.symbols[name] for name in ("d1", "l1", "l2", "d4",
                                                              "d5"))
        self.steer_attachment.set_pos(self.wheel_attachment, d1 * self.x)
        self.body.masscenter.set_pos(self.wheel_attachment, l1 * self.x + l2 * self.z)
        self.saddle.set_pos(self.wheel_attachment, d4 * self.x + d5 * self.z)
        self.body.masscenter.set_vel(self.frame, 0)
        self.steer_attachment.set_vel(self.frame, 0)
        self.wheel_attachment.set_vel(self.frame, 0)
        self.saddle.set_vel(self.frame, 0)

    @property
    def steer_axis(self) -> Vector:
        """Steer axis expressed in the rear frame."""
        return self.z

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
