"""Mixin classes providing common properties for models."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sympy.physics.mechanics import Point, ReferenceFrame, RigidBody, Vector
from sympy.physics.mechanics._system import System

try:
    from symmeplot import PlotBody

    if TYPE_CHECKING:
        from symmeplot.plot_base import PlotBase
except ImportError:  # pragma: no cover
    PlotBase, PlotBody = None, None


class NewtonianBodyMixin:
    """Mixin class adding a Newtonian body to a model."""

    def _define_objects(self) -> None:
        """Define the objects of the model."""
        super()._define_objects()
        body = RigidBody(self.name)
        self._system = System.from_newtonian(body)

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the symbols used in defining the body."""
        body = self.body
        inertia_matrix = body.central_inertia.to_matrix(body.frame)
        descriptions = {
            body.mass: f"Mass of body: '{body.name}'.",
        }
        for i, axis in enumerate("xyz"):
            for j, axis2 in enumerate("xyz"):
                descriptions[inertia_matrix[i, j]] = (f"Inertia scalar {axis}{axis2} of"
                                                      f" body: '{body.name}'.")
        return {obj: desc for obj, desc in descriptions.items() if obj}  # Drop zeros

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

    def get_plot_objects(self, inertial_frame: ReferenceFrame, zero_point: Point
                         ) -> list[PlotBase]:
        """Get the symmeplot plot objects."""
        objects = super().get_plot_objects(inertial_frame, zero_point)
        return [*objects, PlotBody(inertial_frame, zero_point, self.body)]
