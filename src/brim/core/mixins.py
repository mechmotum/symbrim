from __future__ import annotations

from typing import TYPE_CHECKING

from sympy.physics.mechanics import RigidBody, System

if TYPE_CHECKING:
    from sympy.physics.mechanics import ReferenceFrame, Vector


class NewtonianBodyMixin:
    """Mixin class adding a Newtonian body to a model."""

    def define_objects(self) -> None:
        """Define the objects of the model."""
        body: RigidBody = RigidBody(self.name)
        self._system: System = System.from_newtonian(body)
        super().define_objects()

    @property
    def system(self) -> System:
        """System of the model."""
        return self._system

    @property
    def body(self) -> RigidBody:
        """The body representing the model."""
        return self.system.bodies[0]

    @property
    def frame(self) -> ReferenceFrame:
        """Reference frame of the model."""
        return self.body.frame

    @property
    def x(self) -> Vector:
        """X-axis of model."""
        return self.frame.x

    @property
    def y(self) -> Vector:
        """Y-axis of model."""
        return self.frame.y

    @property
    def z(self) -> Vector:
        """Z-axis of model."""
        return self.frame.z
