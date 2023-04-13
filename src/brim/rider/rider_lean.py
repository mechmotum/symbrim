from __future__ import annotations

from typing import TYPE_CHECKING

from sympy import Symbol
from sympy.physics.mechanics import Point

from brim.core import ModelBase, NewtonianBodyMixin

if TYPE_CHECKING:
    from sympy.physics.mechanics import Vector
__all__ = ["RiderLean"]


class RiderLean(NewtonianBodyMixin, ModelBase):
    """Rider lean model."""

    @property
    def actuator(self):  # pragma: no cover
        """Actuator between the rear frame and the rider."""
        return self._actuator

    @actuator.setter
    def actuator(self, actuator) -> None:  # pragma: no cover
        raise NotImplementedError("Support for ActuatorBase is needed.")

    @property
    def lean_point(self):
        """Point about which the rider leans defined w.r.t. the rider."""
        return self._lean_point

    @property
    def lean_axis(self):
        """Lean axis expressed in the leaning rider's frame."""
        return self._lean_axis

    @lean_axis.setter
    def lean_axis(self, lean_axis: Vector) -> None:
        try:
            lean_axis.express(self.frame)
        except AttributeError or ValueError as e:
            raise ValueError(f"The lean axis {lean_axis!r} must be a Vector expressable"
                             f" in the leaning rider frame {self.frame!r}.") from e
        self._lean_axis = lean_axis

    @property
    def descriptions(self) -> dict[Symbol, str]:
        """Descriptions of the symbols of the rider lean model."""
        return {
            **super().descriptions,
            self.symbols["d_lp"]: f"Distance of the {self.lean_point} from the rear "
                                  f"frame center of mass along the z frames axis.",
        }

    def define_objects(self) -> None:
        """Define the objects of the rider lean."""
        super().define_objects()
        self._actuator = None
        self._lean_axis = self.x
        self._lean_point = Point(self._add_prefix("lean_point"))
        self.symbols["d_lp"] = Symbol(self._add_prefix("d_lp"))

    def define_kinematics(self) -> None:
        """Define the kinematics of the rider lean."""
        super().define_kinematics()
        self._lean_point.set_pos(self.body.masscenter, self.symbols["d_lp"] * self.z)

    def define_loads(self) -> None:
        """Define the loads of the rider lean."""
        super().define_loads()
        # TODO: Add actuator loads.
