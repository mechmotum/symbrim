"""Module containing the models of the ground."""
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from sympy.physics.mechanics import Point, ReferenceFrame, RigidBody, Vector, cross
from sympy.physics.mechanics._system import System

from brim.core import ModelBase

if TYPE_CHECKING:
    from sympy import Expr

__all__ = ["GroundBase", "FlatGround"]


class GroundBase(ModelBase):
    """Base class for the ground."""

    def _define_objects(self) -> None:
        """Define the objects of the ground."""
        super()._define_objects()
        self._body = RigidBody(self.name)
        self._body.masscenter = Point(self._add_prefix("origin"))
        self._system = System.from_newtonian(self.body)

    def _define_kinematics(self) -> None:
        """Define the kinematics of the ground."""
        super()._define_kinematics()
        self.origin.set_vel(self.frame, 0)

    @property
    def body(self) -> RigidBody:
        """The body representing the ground."""
        return self._body

    @property
    def frame(self) -> ReferenceFrame:
        """Frame fixed to the ground."""
        return self.body.frame

    @abstractmethod
    def get_normal(self, position: Point | tuple[Expr, Expr]) -> Vector:
        """Get normal vector of the ground."""

    @abstractmethod
    def get_tangent_vectors(self, position: Point | tuple[Expr, Expr]
                            ) -> tuple[Vector, Vector]:
        """Get tangent vectors of the ground plane."""

    @abstractmethod
    def set_point_pos(self, point: Point, position: tuple[Expr, Expr]) -> None:
        """Locate a point on the ground."""

    @property
    def origin(self) -> Point:
        """Origin of the ground."""
        return self.body.masscenter


class FlatGround(GroundBase):
    """Flat ground."""

    def __init__(self, name: str, normal: str = "-z") -> None:
        """Initialize the flat ground.

        Parameters
        ----------
        name : str
            Name of the ground.
        normal : str, optional
            Normal vector of the ground. Options are:
            - "+x", "-x", "+y", "-y", "+z", "-z"
            The default is "-z".

        """
        super().__init__(name)
        self._normal = normal

    def _define_objects(self) -> None:
        """Define the objects of the ground."""
        super()._define_objects()
        if self._normal[0] == "-":
            self._normal = self._normal[1:]
            times = -1
        else:
            times = 1
            if self._normal[0] == "+":
                self._normal = self._normal[1:]
        self._normal = times * self.frame[self._normal]
        if cross(self._normal, self.frame.x) == 0:
            self._planar_vectors = (self.frame.y, self.frame.z)
        elif cross(self._normal, self.frame.y) == 0:
            self._planar_vectors = (self.frame.x, self.frame.z)
        else:
            self._planar_vectors = (self.frame.x, self.frame.y)

    def get_normal(self, position: Point | tuple[Expr, Expr]) -> Vector:
        """Get normal vector of the ground."""
        return self._normal  # type: ignore

    def get_tangent_vectors(self, position: Point | tuple[Expr, Expr]
                            ) -> tuple[Vector, Vector]:
        """Get tangent vectors of the ground plane."""
        return self._planar_vectors

    def set_point_pos(self, point: Point, position: tuple[Expr, Expr]) -> None:
        """Locate a point on the ground."""
        point.set_pos(self.origin, position[0] * self._planar_vectors[0] +
                      position[1] * self._planar_vectors[1])
