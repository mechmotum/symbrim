"""Module containing tyre models for bicycles."""
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from sympy.physics.mechanics import System, cross

from brim.core import ModelBase

if TYPE_CHECKING:

    from brim.bicycle.grounds import GroundBase
    from brim.bicycle.wheels import WheelBase

__all__ = ["TyreModelBase", "NonHolonomicTyreModel"]


class TyreModelBase(ModelBase):
    """Base class for the tyre models."""

    @property
    def system(self) -> System:
        """System of the tyre model."""
        return self._system

    def define_objects(self) -> None:
        """Define the objects of the tyre model."""
        self._system = System()

    def define_kinematics(self) -> None:
        """Define the kinematics of the tyre model."""

    def define_loads(self) -> None:
        """Define the loads of the tyre model."""

    @abstractmethod
    def compute(self, ground: GroundBase, wheel: WheelBase, on_ground: bool
                ) -> None:
        """Compute the tyre model.

        Parameters
        ----------
        ground : GroundBase
            Ground model.
        wheel : WheelBase
            Wheel model.
        on_ground : bool
            Boolean whether the wheel is already defined as touching the ground.

        """


class NonHolonomicTyreModel(TyreModelBase):
    """Tyre model based on non-holonomic constraints."""

    def compute(self, ground: GroundBase, wheel: WheelBase, on_ground: bool
                ) -> None:
        """Compute the tyre model.

        Parameters
        ----------
        ground : GroundBase
            Ground model.
        wheel : WheelBase
            Wheel model.
        on_ground : bool
            Boolean whether the wheel is already defined as touching the ground.

        """
        v0 = wheel.center.vel(ground.frame) + cross(
            wheel.frame.ang_vel_in(ground.frame),
            wheel.contact_point.pos_from(wheel.center)
        )
        self.system.add_nonholonomic_constraints(
            v0.dot(ground.planar_vectors[0]), v0.dot(ground.planar_vectors[1]))
        if not on_ground:
            self.system.add_holonomic_constraints(
                wheel.contact_point.pos_from(ground.origin).dot(ground.normal))
