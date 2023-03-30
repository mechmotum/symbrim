"""Module containing the models of the rear frame of a bicycle."""
from __future__ import annotations

from abc import abstractmethod
from typing import Any

from sympy import Symbol, symbols
from sympy.physics.mechanics import Point, Vector, inertia

from brim.core import ModelBase, NewtonianBodyMixin

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


class RigidRearFrame(RearFrameBase):
    """Rigid rear frame."""

    def __new__(cls, name: str, *args, formulation="moore", **kwargs):
        """Create a new instance of the rear frame.

        Parameters
        ----------
        name : str
            Name of the rear frame.
        formulation : str, optional
            Formulation of the rear frame, by default "moore".

        """
        if formulation == "moore":
            cls = RigidRearFrameMoore
        else:
            raise NotImplementedError(f"Formulation '{formulation}' has not been "
                                      f"implemented.")
        return super().__new__(cls)

    def define_objects(self):
        """Define the objects of the rear frame."""
        super().define_objects()
        self.body.central_inertia = inertia(self.body.frame,
                                            *symbols(self._add_prefix("ixx iyy izz")),
                                            izx=Symbol(self._add_prefix("izx")))
        self._wheel_attachment = Point("wheel_attachment")

    def define_kinematics(self):
        """Define the kinematics of the rear frame."""
        super().define_kinematics()
        self.wheel_attachment.set_vel(self.frame, 0)

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


class RigidRearFrameMoore(RigidRearFrame):
    """Rigid rear frame model based on Moore's formulation."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the rear frame."""
        return {
            **super().descriptions,
            self.lengths[0]: "Perpendicular distance from the steer axis to the center "
                             "of the rear wheel (rear offset).",
            self.lengths[1]: "Distance in the rear frame x drection from the rear "
                             "wheel center to the center of mass of the rear frame.",
            self.lengths[2]: "Distance in the rear frame z drection from the rear "
                             "wheel center to the center of mass of the rear frame.",
        }

    def define_objects(self):
        """Define the objects of the rear frame."""
        super().define_objects()
        self.lengths = list(symbols(self._add_prefix("d1 l1 l2")))
        self._steer_attachment = Point("steer_attachment")

    def define_kinematics(self):
        """Define the kinematics of the rear frame."""
        super().define_kinematics()
        self.steer_attachment.set_pos(self.wheel_attachment,
                                      self.lengths[0] * self.body.x)
        self.body.masscenter.set_pos(self.wheel_attachment,
                                     self.lengths[1] * self.body.x + self.lengths[
                                         2] * self.body.z)
        self.body.masscenter.set_vel(self.frame, 0)
        self.steer_attachment.set_vel(self.frame, 0)
        self.wheel_attachment.set_vel(self.frame, 0)

    @property
    def steer_axis(self) -> Vector:
        """Steer axis expressed in the rear frame."""
        return self.body.z

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
