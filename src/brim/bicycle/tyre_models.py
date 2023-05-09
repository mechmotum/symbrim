"""Module containing tyre models for bicycles."""
from __future__ import annotations

from sympy.physics.mechanics import Point, cross
from sympy.physics.mechanics._system import System

from brim.bicycle.grounds import FlatGround, GroundBase
from brim.bicycle.wheels import KnifeEdgeWheel, ToroidalWheel, WheelBase
from brim.core import ConnectionBase, ModelRequirement

__all__ = ["TyreModelBase", "NonHolonomicTyreModel"]


def _set_pos_contact_point(contact_point: Point, ground: GroundBase, wheel: WheelBase
                           ) -> None:
    """Compute the contact point of the wheel with the ground."""
    if isinstance(ground, FlatGround):
        if isinstance(wheel, KnifeEdgeWheel):
            wheel.center.set_pos(contact_point, wheel.radius * cross(
                wheel.body.y, cross(ground.normal, wheel.body.y)).normalize())
            return
        elif isinstance(wheel, ToroidalWheel):
            wheel.center.set_pos(contact_point, wheel.radius * cross(
                wheel.body.y, cross(ground.normal, wheel.body.y)
            ).normalize() + wheel.transverse_radius * ground.normal)
            return
    raise NotImplementedError(
        f"Computation of the contact point has not been implemented for the combination"
        f" of {type(ground)} and {type(wheel)}.")


class TyreModelBase(ConnectionBase):
    """Base class for the tyre model connectors."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("ground", GroundBase, "Submodel of the ground."),
        ModelRequirement("wheel", WheelBase, "Submodel of the wheel."),
    )
    ground: GroundBase
    wheel: WheelBase

    def define_objects(self) -> None:
        """Define the objects of the tyre model."""
        super().define_objects()
        self._system = System.from_newtonian(self.ground.body)
        self._contact_point = Point(self._add_prefix("contact_point"))
        self._on_ground = False

    @property
    def contact_point(self) -> Point:
        """Point representing the contact point of the wheel with the ground."""
        return self._contact_point

    @property
    def on_ground(self) -> bool:
        """Boolean whether the wheel is already defined as touching the ground."""
        return self._on_ground

    @on_ground.setter
    def on_ground(self, value: bool) -> None:
        self._on_ground = bool(value)


class NonHolonomicTyreModel(TyreModelBase):
    """Tyre model connection based on non-holonomic constraints."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("ground", FlatGround, "Submodel of the ground."),
        ModelRequirement("wheel", (KnifeEdgeWheel, ToroidalWheel),
                         "Submodel of the wheel."),
    )
    ground: FlatGround
    wheel: KnifeEdgeWheel | ToroidalWheel

    def define_kinematics(self) -> None:
        """Define the kinematics of the tyre model."""
        super().define_kinematics()
        _set_pos_contact_point(self.contact_point, self.ground, self.wheel)

    def define_constraints(self) -> None:
        """Define the constraints of the tyre model."""
        super().define_constraints()
        v0 = self.wheel.center.vel(self.ground.frame) + cross(
            self.wheel.frame.ang_vel_in(self.ground.frame),
            self.contact_point.pos_from(self.wheel.center)
        )
        self.system.add_nonholonomic_constraints(
            v0.dot(self.ground.planar_vectors[0]),
            v0.dot(self.ground.planar_vectors[1]))
        if not self.on_ground:
            self.system.add_holonomic_constraints(
                self.contact_point.pos_from(self.ground.origin).dot(self.ground.normal))
