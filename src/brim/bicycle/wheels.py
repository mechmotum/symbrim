"""Module containing the wheel models."""
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from sympy import Symbol, symbols
from sympy.physics.mechanics import Point, inertia

from brim.core import ModelBase, NewtonianBodyMixin

if TYPE_CHECKING:
    from sympy.physics.mechanics import Vector


__all__ = ["WheelBase", "KnifeEdgeWheel", "ToroidalWheel"]


class WheelBase(NewtonianBodyMixin, ModelBase):
    """Wheel base class."""

    def define_objects(self) -> None:
        """Define the objects of the wheel."""
        super().define_objects()

    @property
    @abstractmethod
    def center(self) -> Point:
        """Point representing the center of the wheel."""

    @property
    @abstractmethod
    def rotation_axis(self) -> Vector:
        """Rotation axis of the wheel."""


class KnifeEdgeWheel(WheelBase):
    """Knife edge wheel."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the wheel."""
        return {
            **super().descriptions,
            self.radius: self.radius.__doc__,
        }

    @property
    def radius(self) -> Symbol:
        """Radius of the wheel."""
        return self.symbols["r"]

    def define_objects(self) -> None:
        """Define the objects of the wheel."""
        super().define_objects()
        self.body.central_inertia = inertia(self.body.frame,
                                            *symbols(self._add_prefix("ixx iyy ixx")))
        self.symbols["r"] = Symbol(self._add_prefix("r"))

    @property
    def center(self) -> Point:
        """Point representing the center of the wheel."""
        return self.body.masscenter

    @property
    def rotation_axis(self) -> Vector:
        """Rotation axis of the wheel."""
        return self.body.y


class ToroidalWheel(WheelBase):
    """Toroidal shaped wheel."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the wheel."""
        return {
            **super().descriptions,
            self.radius: self.radius.__doc__,
            self.transverse_radius: self.transverse_radius.__doc__
        }

    @property
    def radius(self) -> Symbol:
        """Radius of the wheel."""
        return self.symbols["r"]

    @property
    def transverse_radius(self) -> Symbol:
        """Transverse radius of curvature of the crown of the wheel."""
        return self.symbols["tr"]

    def define_objects(self) -> None:
        """Define the objects of the wheel."""
        super().define_objects()
        self.body.central_inertia = inertia(self.body.frame,
                                            *symbols(self._add_prefix("ixx iyy ixx")))
        self.symbols["r"] = Symbol(self._add_prefix("r"))
        self.symbols["tr"] = Symbol(self._add_prefix("tr"))

    @property
    def center(self) -> Point:
        """Point representing the center of the wheel."""
        return self.body.masscenter

    @property
    def rotation_axis(self) -> Vector:
        """Rotation axis of the wheel."""
        return self.body.y
