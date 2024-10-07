"""Module containing a simplified rider lean model."""
from __future__ import annotations

from sympy import Matrix, Symbol
from sympy.physics.mechanics import PinJoint, Point, System, Vector, dynamicsymbols

from symbrim.bicycle.rear_frames import RearFrameBase
from symbrim.core import ConnectionBase, ModelBase, ModelRequirement, NewtonianBodyMixin

__all__ = ["RiderLean", "RiderLeanConnection"]


class RiderLean(NewtonianBodyMixin, ModelBase):
    """Rider lean model."""

    @property
    def lean_point(self) -> Point:
        """Point about which the rider leans defined w.r.t. the rider."""
        return self._lean_point

    @property
    def lean_axis(self) -> Vector:
        """Lean axis expressed in the leaning rider's frame."""
        return self._lean_axis

    @lean_axis.setter
    def lean_axis(self, lean_axis: Vector) -> None:
        try:
            lean_axis.express(self.frame)
        except (AttributeError, ValueError) as e:
            raise ValueError(f"The lean axis {lean_axis!r} must be a Vector expressable"
                             f" in the leaning rider frame {self.frame!r}.") from e
        self._lean_axis = lean_axis

    @property
    def descriptions(self) -> dict[object, str]:
        """Descriptions of the symbols of the rider lean model."""
        return {
            **super().descriptions,
            self.symbols["d_lp"]: f"Distance of the {self.lean_point} from the rear "
                                  f"frame center of mass along the z frames axis.",
        }

    def _define_objects(self) -> None:
        """Define the objects of the rider lean."""
        super()._define_objects()
        self._lean_axis = self.x
        self._lean_point = Point(self._add_prefix("lean_point"))
        self.symbols["d_lp"] = Symbol(self._add_prefix("d_lp"))

    def _define_kinematics(self) -> None:
        """Define the kinematics of the rider lean."""
        super()._define_kinematics()
        self._lean_point.set_pos(self.body.masscenter, self.symbols["d_lp"] * self.z)


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
            lean_axis.express(self.rear_frame.saddle.frame)
        except (AttributeError, ValueError) as e:
            raise ValueError(f"The lean axis {lean_axis!r} must be a Vector expressable"
                             f" in the rear frame {self.rear_frame!r}.") from e
        self._lean_axis = lean_axis

    @property
    def lean_point(self) -> Point:
        """Point about which the rider leans defined w.r.t. the rear frame."""
        return self._lean_point

    @property
    def descriptions(self) -> dict[object, str]:
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

    def _define_objects(self) -> None:
        """Define the objects of the rider lean connection for the rear frame."""
        super()._define_objects()
        self._system = System(self.rear_frame.system.frame,
                              self.rear_frame.system.fixed_point)
        self._lean_axis = self.rear_frame.saddle.frame.x
        self._lean_point = Point(self._add_prefix("lean_point"))
        self.symbols["d_lp_x"] = Symbol(self._add_prefix("d_lp_x"))
        self.symbols["d_lp_z"] = Symbol(self._add_prefix("d_lp_z"))
        self.q = Matrix([dynamicsymbols(self._add_prefix("q_rl"))])
        self.u = Matrix([dynamicsymbols(self._add_prefix("u_rl"))])

    def _define_kinematics(self) -> None:
        """Define the kinematics of the rider lean connection for the rear frame."""
        super()._define_kinematics()
        saddle = self.rear_frame.saddle
        self.lean_point.set_pos(saddle.point,
                                self.symbols["d_lp_x"] * saddle.frame.x +
                                self.symbols["d_lp_z"] * saddle.frame.z)
        self.system.add_joints(
            PinJoint("rider_lean_joint", saddle.to_valid_joint_arg(), self.rider.body,
                     self.q[0], self.u[0], self.lean_point, self.rider.lean_point,
                     self.lean_axis, self.rider.lean_axis)
        )
