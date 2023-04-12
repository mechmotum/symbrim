from __future__ import annotations

from typing import TYPE_CHECKING

from sympy import Matrix, Symbol
from sympy.physics.mechanics import PinJoint, Point, Vector, dynamicsymbols

from brim.core import ModelBase, ModelRequirement, NewtonianBodyMixin

if TYPE_CHECKING:
    from sympy import Basic
__all__ = ["RiderLeanMixin", "RiderLean"]


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
        if not isinstance(lean_axis, Vector):
            raise TypeError("The lean axis must be a Vector.")
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
        # TODO add actuator support


class RiderLeanMixin:
    """Mixin that adds rider lean support to the RearFrameBase."""

    required_models = (
        ModelRequirement("rider", RiderLean, "Leaning rider model."),
    )

    @property
    def lean_axis(self) -> Vector:
        """Lean axis expressed in the rear frame."""
        return self._lean_axis

    @lean_axis.setter
    def lean_axis(self, lean_axis: Vector) -> None:
        if not isinstance(lean_axis, Vector):
            raise TypeError("The lean axis must be a Vector.")
        self._lean_axis = lean_axis

    @property
    def lean_point(self) -> Point:
        """Point about which the rider leans defined w.r.t. the rear frame."""
        return self._lean_point

    @property
    def descriptions(self) -> dict[Basic, str]:
        """Descriptions of the symbols of the rider lean mixin for the rear frame."""
        desc = {
            **super().descriptions,
            self.symbols["d_lp_x"]: f"Distance of the {self.lean_point} from the rear "
                                    f"frame center of mass along the x frames axis.",
            self.symbols["d_lp_z"]: f"Distance of the {self.lean_point} from the rear "
                                    f"frame center of mass along the z frames axis.",
            self.q[0]: "Rider lean angle in the roll direction of the rear frame."
        }
        desc.update({ui: f"Generalized speed of the {desc[qi].lower()}"
                     for qi, ui in zip(self.q, self.u)})
        return desc

    def define_objects(self):
        """Define the objects of the rider lean mixin for the rear frame."""
        super().define_objects()
        self._lean_axis = self.x
        self._lean_point = Point(self._add_prefix("lean_point"))
        self.symbols["d_lp_x"] = Symbol(self._add_prefix("d_lp_x"))
        self.symbols["d_lp_z"] = Symbol(self._add_prefix("d_lp_z"))
        self.q: Matrix = Matrix([dynamicsymbols(self._add_prefix("q_rl"))])
        self.u: Matrix = Matrix([dynamicsymbols(self._add_prefix("u_rl"))])

    def define_kinematics(self):
        """Define the kinematics of the rider lean mixin for the rear frame."""
        super().define_kinematics()
        self.lean_point.set_pos(self.body.masscenter, self.symbols["d_lp_x"] * self.x +
                                self.symbols["d_lp_z"] * self.z)
        self.system.add_joints(
            PinJoint("rider_lean_joint", self.body, self.rider.body, self.q[0],
                     self.u[0], self.lean_point, self.rider.lean_point, self.lean_axis,
                     self.rider.lean_axis)
        )
