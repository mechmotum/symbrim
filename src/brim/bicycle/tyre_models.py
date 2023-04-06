"""Module containing tyre models for bicycles."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sympy.physics.mechanics import System, cross

from brim.bicycle.grounds import GroundBase
from brim.core import Connection, ModelBase

if TYPE_CHECKING:
    from brim.bicycle.wheels import WheelBase

__all__ = ["TyreModelBase", "NonHolonomicTyreModel"]


class TyreModelBase(ModelBase):
    """Base class for the tyre models."""

    requirements: tuple[Connection, ...] = (
        Connection("ground", GroundBase,
                   "Ground model w.r.t. which the tyre model is defined."),
        Connection("wheel", ModelBase, "Wheel model to which the tyre is attached."),
    )
    ground: GroundBase
    wheel: WheelBase

    @property
    def system(self) -> System:
        """System of the tyre model."""
        return self._system

    def define_objects(self) -> None:
        """Define the objects of the tyre model."""
        super().define_objects()
        self._system = System()
        self.on_ground: bool = False

    def define_kinematics(self) -> None:
        """Define the kinematics of the tyre model."""
        super().define_kinematics()


class NonHolonomicTyreModel(TyreModelBase):
    """Tyre model based on non-holonomic constraints."""

    def define_loads(self) -> None:
        """Define the loads of the tyre model."""
        super().define_loads()
        print("here in nonholonomic")
        v0 = self.wheel.center.vel(self.ground.frame) + cross(
            self.wheel.frame.ang_vel_in(self.ground.frame),
            self.wheel.contact_point.pos_from(self.wheel.center)
        )
        self.system.add_nonholonomic_constraints(
            v0.dot(self.ground.planar_vectors[0]), v0.dot(self.ground.planar_vectors[1])
        )
        if not self.on_ground:
            self.system.add_holonomic_constraints(
                self.wheel.contact_point.pos_from(self.ground.origin).dot(
                    self.ground.normal))

    define_loads.order = 1  # Uses a connection so should be defined after parent.
