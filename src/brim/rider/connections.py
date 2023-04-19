"""Module containing the connections between the rider and the bicycle."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sympy import Matrix, Symbol
from sympy.physics.mechanics import PinJoint, Point, dynamicsymbols
from sympy.physics.mechanics._system import System

from brim.bicycle import RearFrameBase
from brim.core import ConnectionBase, ModelRequirement
from brim.rider.rider_lean import RiderLean

if TYPE_CHECKING:
    from sympy.physics.mechanics import Vector
__all__ = ["RiderLeanConnection"]


class RiderLeanConnection(ConnectionBase):
    """Mixin that adds rider lean support to the RearFrameBase."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("rider", RiderLean, "Leaning rider model."),
        ModelRequirement("rear_frame", RearFrameBase, "Rear frame model."),
    )
    rider: RiderLean
    rear_frame: RearFrameBase

    @property
    def lean_axis(self) -> Vector:
        """Lean axis expressed in the rear frame."""
        return self._lean_axis

    @lean_axis.setter
    def lean_axis(self, lean_axis: Vector) -> None:
        try:
            lean_axis.express(self.rear_frame.frame)
        except AttributeError or ValueError as e:
            raise ValueError(f"The lean axis {lean_axis!r} must be a Vector expressable"
                             f" in the rear frame {self.rear_frame!r}.") from e
        self._lean_axis = lean_axis

    @property
    def lean_point(self) -> Point:
        """Point about which the rider leans defined w.r.t. the rear frame."""
        return self._lean_point

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the symbols of the rider lean connection."""
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
        """Define the objects of the rider lean connection for the rear frame."""
        super().define_objects()
        self._system = System()
        self._lean_axis = self.rear_frame.x
        self._lean_point = Point(self._add_prefix("lean_point"))
        self.symbols["d_lp_x"] = Symbol(self._add_prefix("d_lp_x"))
        self.symbols["d_lp_z"] = Symbol(self._add_prefix("d_lp_z"))
        self.q: Matrix = Matrix([dynamicsymbols(self._add_prefix("q_rl"))])
        self.u: Matrix = Matrix([dynamicsymbols(self._add_prefix("u_rl"))])

    def define_kinematics(self):
        """Define the kinematics of the rider lean connection for the rear frame."""
        super().define_kinematics()
        self.lean_point.set_pos(self.rear_frame.body.masscenter,
                                self.symbols["d_lp_x"] * self.rear_frame.x +
                                self.symbols["d_lp_z"] * self.rear_frame.z)
        self.system.add_joints(
            PinJoint("rider_lean_joint", self.rear_frame.body, self.rider.body,
                     self.q[0], self.u[0], self.lean_point, self.rider.lean_point,
                     self.lean_axis, self.rider.lean_axis)
        )
