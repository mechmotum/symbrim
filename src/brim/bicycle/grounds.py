"""Module containing the models of the ground."""
from __future__ import annotations

from abc import abstractmethod

from sympy.physics.mechanics import (
    Point,
    ReferenceFrame,
    RigidBody,
    System,
    Vector,
    cross,
)

from brim.core import ModelBase

__all__ = ["GroundBase", "FlatGround"]


class GroundBase(ModelBase):
    """Base class for the ground."""

    def define_objects(self) -> None:
        """Define the objects of the ground."""
        super().define_objects()
        self._body = RigidBody(self.name)
        self._body.masscenter = Point(self.add_prefix("origin"))
        self._system = System.from_newtonian(self.body)

    def define_kinematics(self) -> None:
        """Define the kinematics of the ground."""
        super().define_kinematics()
        self.origin.set_vel(self.frame, 0)

    def define_loads(self) -> None:
        """Define the loads acting upon the ground."""
        super().define_loads()

    @property
    def body(self) -> RigidBody:
        """The body representing the ground."""
        return self._body

    @property
    @abstractmethod
    def frame(self) -> ReferenceFrame:
        """Frame fixed to the ground."""

    @property
    @abstractmethod
    def normal(self) -> Vector:
        """Normal vector of the ground."""

    @property
    @abstractmethod
    def planar_vectors(self) -> tuple[Vector, Vector]:
        """Planar vectors of the ground."""

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
        if normal[0] == "-":
            normal = normal[1:]
            times = -1
        else:
            times = 1
            if normal[0] == "+":
                normal = normal[1:]
        self._normal = times * self.frame[normal]
        if cross(self._normal, self.frame.x) == 0:
            self._planar_vectors = (self.frame.y, self.frame.z)
        elif cross(self._normal, self.frame.y) == 0:
            self._planar_vectors = (self.frame.x, self.frame.z)
        else:
            self._planar_vectors = (self.frame.x, self.frame.y)

    @property
    def frame(self) -> ReferenceFrame:
        """Frame fixed to the ground."""
        return self.body.frame

    @property
    def normal(self) -> Vector:
        """Normal vector of the ground."""
        return self._normal

    @property
    def planar_vectors(self) -> tuple[Vector, Vector]:
        """Planar vectors of the ground."""
        return self._planar_vectors
