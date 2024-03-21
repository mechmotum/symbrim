"""Module containing tire models for bicycles."""
from __future__ import annotations

from typing import Any

from sympy import MutableDenseMatrix as Matrix
from sympy.physics.mechanics import Point, System, Vector, cross, dynamicsymbols

from brim.bicycle.grounds import FlatGround, GroundBase
from brim.bicycle.wheels import KnifeEdgeWheel, ToroidalWheel, WheelBase
from brim.core import ConnectionBase, ModelRequirement
from brim.utilities.utilities import check_zero

__all__ = ["TireBase", "NonHolonomicTire"]


class TireBase(ConnectionBase):
    """Base class for the tire model connectors."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("ground", GroundBase, "Submodel of the ground."),
        ModelRequirement("wheel", WheelBase, "Submodel of the wheel."),
    )
    ground: GroundBase
    wheel: WheelBase

    def _set_pos_contact_point(self) -> None:
        """Compute the contact point of the wheel with the ground."""
        if isinstance(self.ground, FlatGround):
            if isinstance(self.wheel, KnifeEdgeWheel):
                self.wheel.center.set_pos(self.contact_point,
                                          self.wheel.radius * self.upward_radial_axis)
                return
            elif isinstance(self.wheel, ToroidalWheel):
                self.wheel.center.set_pos(
                    self.contact_point,
                    self.wheel.radius * self.upward_radial_axis +
                    self.wheel.transverse_radius * self.ground.get_normal(
                        self.contact_point))
                return
        raise NotImplementedError(
            f"Computation of the contact point has not been implemented for the "
            f"combination of {type(self.ground)} and {type(self.wheel)}.")

    def _define_objects(self) -> None:
        """Define the objects of the tire model."""
        super()._define_objects()
        self._system = System.from_newtonian(self.ground.body)
        self._contact_point = Point(self._add_prefix("contact_point"))
        self._on_ground = None
        self._upward_radial_axis = None

    @property
    def upward_radial_axis(self) -> Vector:
        """Wheel radial axis pointing upward from the contact point to the wheel center.

        Explanation
        -----------
        To possibly simplify the equations of motion, one can overwrite the axis used
        to compute the location of the contact point with respect to the wheel center.
        This axis should be normalized. For a knife-edge wheel, one could express the
        vector from the wheel center to the contact point of the ground as
        ``wheel.radius * upward_radial_axis``.
        """
        if self._upward_radial_axis is None:
            self._upward_radial_axis = cross(
                self.wheel.rotation_axis,
                cross(self.ground.get_normal(self.contact_point),
                      self.wheel.rotation_axis)
            ).normalize()
        return self._upward_radial_axis

    @upward_radial_axis.setter
    def upward_radial_axis(self, axis: Vector) -> None:
        name = "The upward radial axis of the wheel"
        if not isinstance(axis, Vector):
            raise TypeError(f"{name} should be a vector, but received a {type(axis)}")
        if not check_zero(axis.magnitude() - 1):
            raise ValueError(f"{name} should be normalized.")
        if not check_zero(axis.dot(self.wheel.rotation_axis)):
            raise ValueError(f"{name} should be perpendicular to the rotation axis.")
        if not check_zero(axis.dot(cross(self.ground.get_normal(self.contact_point),
                                         self.wheel.rotation_axis))):
            raise ValueError(
                f"{name} should be perpendicular to an axis that is perpendicular to "
                f"both the normal vector and rotation axis.")
        self._upward_radial_axis = axis

    @property
    def contact_point(self) -> Point:
        """Point representing the contact point of the wheel with the ground."""
        return self._contact_point

    @property
    def on_ground(self) -> bool:
        """Boolean whether the wheel is already defined as touching the ground."""
        if self._on_ground is None:
            try:
                normal = self.ground.get_normal(self.contact_point)
                distance = self.contact_point.pos_from(self.ground.origin).dot(normal)
                self._on_ground = check_zero(distance)
            except (AttributeError, ValueError):
                self._on_ground = False
        return self._on_ground

    @on_ground.setter
    def on_ground(self, value: bool) -> None:
        self._on_ground = bool(value)


class NonHolonomicTire(TireBase):
    """Tire model connection based on non-holonomic constraints."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("ground", FlatGround, "Submodel of the ground."),
        ModelRequirement("wheel", (KnifeEdgeWheel, ToroidalWheel),
                         "Submodel of the wheel."),
    )
    ground: FlatGround
    wheel: KnifeEdgeWheel | ToroidalWheel

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self._compute_normal_force = False

    @property
    def compute_normal_force(self) -> bool:
        """Boolean whether the normal force should be computed."""
        return self._compute_normal_force

    @compute_normal_force.setter
    def compute_normal_force(self, value: bool) -> None:
        self._compute_normal_force = bool(value)

    @property
    def descriptions(self) -> dict[Any, str]:
        """Dictionary of descriptions of the non-holonomic tire model's attributes."""
        descriptions = super().descriptions
        if self.compute_normal_force:
            descriptions.update({
                self.u[0]: "Auxiliary generalized speed to determine the normal force.",
                self.symbols["Fz"]: "Negative of the normal force of the tire model.",
            })
        return descriptions

    def _define_objects(self) -> None:
        """Define the objects of the tire model."""
        super()._define_objects()
        if self.compute_normal_force:
            self.u = Matrix([dynamicsymbols(self._add_prefix("uaux_z"))])
            self.symbols["Fz"] = dynamicsymbols(self._add_prefix("Fz"))

    def _define_kinematics(self) -> None:
        """Define the kinematics of the tire model."""
        super()._define_kinematics()
        self._set_pos_contact_point()
        if self.on_ground:
            self.wheel.center.set_vel(
                self.ground.frame,
                cross(self.wheel.frame.ang_vel_in(self.ground.frame),
                      self.wheel.center.pos_from(self.contact_point)))
        if self.compute_normal_force:
            direction = -self.ground.get_normal(self.contact_point)
            if self.on_ground:
                direction = -direction
            self.auxiliary_handler.add_noncontributing_force(
                self.contact_point, direction, self.u[0], self.symbols["Fz"])

    def _define_constraints(self) -> None:
        """Define the constraints of the tire model."""
        super()._define_constraints()
        normal = self.ground.get_normal(self.contact_point)
        tangent_vectors = self.ground.get_tangent_vectors(self.contact_point)
        v0 = self.wheel.center.pos_from(self.ground.origin).dt(self.ground.frame
                                                               ) + cross(
            self.wheel.frame.ang_vel_in(self.ground.frame),
            self.contact_point.pos_from(self.wheel.center)
        )
        self.system.add_nonholonomic_constraints(
            v0.dot(tangent_vectors[0]), v0.dot(tangent_vectors[1]))
        if not self.on_ground:
            self.system.add_holonomic_constraints(
                self.contact_point.pos_from(self.ground.origin).dot(normal))
            if self.compute_normal_force:
                self.system.velocity_constraints = [
                    self.system.holonomic_constraints[0].diff(dynamicsymbols._t) +
                    self.auxiliary_handler.get_auxiliary_velocity(
                        self.contact_point).dot(normal),
                    *self.system.nonholonomic_constraints
                ]
