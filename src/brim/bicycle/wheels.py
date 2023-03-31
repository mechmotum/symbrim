"""Module containing the wheel models."""
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from sympy import Symbol, symbols
from sympy.physics.mechanics import Point, cross, inertia

from brim.bicycle.tyre_models import TyreModelBase
from brim.core import ModelBase, NewtonianBodyMixin, Requirement

if TYPE_CHECKING:
    from sympy.physics.mechanics import Vector

    from brim.bicycle.grounds import GroundBase

__all__ = ["WheelBase", "KnifeEdgeWheel", "ToroidalWheel"]


class WheelBase(NewtonianBodyMixin, ModelBase):
    """Wheel base class."""

    requirements: tuple[Requirement, ...] = (
        Requirement("tyre_model", TyreModelBase, "Tyre model of the wheel."),
    )
    tyre_model: TyreModelBase

    def define_objects(self) -> None:
        """Define the objects of the wheel."""
        super().define_objects()
        self._contact_point = Point(self._add_prefix("contact_point"))

    @property
    @abstractmethod
    def center(self) -> Point:
        """Point representing the center of the wheel."""

    @property
    @abstractmethod
    def rotation_axis(self) -> Vector:
        """Rotation axis of the wheel."""

    @property
    def contact_point(self) -> Point:
        """Point representing the contact point of the wheel with the ground."""
        return self._contact_point

    @abstractmethod
    def compute_contact_point(self, ground: GroundBase) -> None:
        """Set the position of the contact point.

        Explanation
        -----------
        This method should be part of the parent model to set the position of the wheel
        contact point with the ground.
        """

    def compute_tyre_model(self, ground: GroundBase, on_ground: bool) -> None:
        """Compute the tyre model."""
        self.tyre_model.compute(ground, self, on_ground)


class KnifeEdgeWheel(WheelBase):
    """Knife edge wheel."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the wheel."""
        return {self.radius: self.radius.__doc__}

    @property
    def radius(self) -> Symbol:
        """Radius of the wheel."""
        return self.symbols["r"]

    def define_objects(self) -> None:
        """Define the objects of the wheel."""
        super().define_objects()
        self.body.central_inertia = inertia(self.body.frame,
                                            *symbols(self._add_prefix("ixx iyy ixx")))
        self.symbols = {"r": Symbol(self._add_prefix("r"))}

    def define_kinematics(self) -> None:
        """Define the kinematics of the wheel."""
        super().define_kinematics()

    def define_loads(self) -> None:
        """Define the loads acting upon the wheel."""
        super().define_loads()

    @property
    def center(self) -> Point:
        """Point representing the center of the wheel."""
        return self.body.masscenter

    @property
    def rotation_axis(self) -> Vector:
        """Rotation axis of the wheel."""
        return self.body.y

    def compute_contact_point(self, ground: GroundBase) -> None:
        """Set the position of the contact point.

        Explanation
        -----------
        This method should be part of the parent model to set the position of the wheel
        contact point with the ground.
        """
        self.center.set_pos(self.contact_point, self.symbols["r"] * cross(
            self.body.y, cross(ground.normal, self.body.y)).normalize())


class ToroidalWheel(KnifeEdgeWheel):
    """Toroidal shaped wheel."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the wheel."""
        return {
            **super().descriptions,
            self.transverse_radius: self.transverse_radius.__doc__
        }

    @property
    def transverse_radius(self) -> Symbol:
        """Transverse radius of the wheel."""
        return self.symbols["tr"]

    def define_objects(self) -> None:
        """Define the objects of the wheel."""
        super().define_objects()
        self.symbols["tr"] = Symbol(self._add_prefix("tr"))

    def compute_contact_point(self, ground: GroundBase) -> None:
        """Set the position of the contact point.

        Explanation
        -----------
        This method should be part of the parent model to set the position of the wheel
        contact point with the ground.
        """
        self.center.set_pos(self.contact_point, self.radius * cross(
            self.body.y, cross(ground.normal, self.body.y)).normalize() +
                            self.transverse_radius * ground.normal)
