"""Module containing the seat connections."""
from __future__ import annotations

from typing import Any

from sympy import Matrix, Symbol, cos, sin
from sympy.physics.mechanics import PinJoint, Point, Vector, dynamicsymbols
from sympy.physics.mechanics._actuator import TorqueActuator
from sympy.physics.mechanics._system import System

from brim.brim.base_connections import SeatBase
from brim.core import LoadGroupBase

__all__ = ["SideLeanSeat", "SideLeanSeatTorque", "SideLeanSeatSpringDamper"]


class SideLeanSeat(SeatBase):
    """Rider lean connection between the rear frame and the pelvis."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.q[0]: "Lean angle.",
            self.u[0]: "Angular lean velocity.",
            self.symbols["alpha"]: "Angle of the rider lean axis.",
        }

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self.q = Matrix([dynamicsymbols(self._add_prefix("q"))])
        self.u = Matrix([dynamicsymbols(self._add_prefix("u"))])
        alpha = Symbol(self._add_prefix("alpha"))
        self.symbols["alpha"] = alpha
        self._frame_lean_axis = (cos(alpha) * self.rear_frame.x -
                                 sin(alpha) * self.rear_frame.z)
        self._pelvis_lean_axis = self.pelvis.x
        self._pelvis_interpoint = None
        self._system = System.from_newtonian(self.rear_frame.body)

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        if self._pelvis_interpoint is None:
            self._pelvis_interpoint = (self.pelvis.left_hip_point.pos_from(
                self.pelvis.body.masscenter) + self.pelvis.right_hip_point.pos_from(
                self.pelvis.body.masscenter)) / 2
        self.system.add_joints(
            PinJoint(
                self._add_prefix("lean_joint"), self.rear_frame.body, self.pelvis.body,
                self.q, self.u, self.rear_frame.saddle, self.pelvis_interpoint,
                self.frame_lean_axis, self.pelvis_lean_axis)
        )

    @property
    def frame_lean_axis(self) -> Vector:
        """Return the lean axis of the rear frame."""
        return self._frame_lean_axis

    @frame_lean_axis.setter
    def frame_lean_axis(self, value: Vector) -> None:
        """Set the lean axis of the rear frame."""
        try:
            value.express(self.rear_frame.frame)
        except ValueError as e:
            raise ValueError("Lean axis must be expressable in the rear frame.") from e
        self._frame_lean_axis = value

    @property
    def pelvis_lean_axis(self) -> Vector:
        """Return the lean axis of the pelvis."""
        return self._pelvis_lean_axis

    @pelvis_lean_axis.setter
    def pelvis_lean_axis(self, value: Vector) -> None:
        """Set the lean axis of the pelvis."""
        try:
            value.express(self.pelvis.frame)
        except ValueError as e:
            raise ValueError(
                "Lean axis must be expressable in the pelvis frame.") from e
        self._pelvis_lean_axis = value

    @property
    def pelvis_interpoint(self) -> Vector | Point | None:
        """Return the rotation point w.r.t. the pelvis.

        Explanation
        -----------
        The pelvis interpoint can either be a vector w.r.t. the the center of mass of
        the pelvis or a point fixed on the pelvis body. This point will also get a
        zero velocity with respect to the saddle.
        """
        return self._pelvis_interpoint

    @pelvis_interpoint.setter
    def pelvis_interpoint(self, value: Vector | Point) -> None:
        try:
            if isinstance(value, Vector):
                value.express(self.pelvis.frame)
            else:
                value.pos_from(self.pelvis.body.masscenter).express(self.pelvis.frame)
        except ValueError as e:
            raise ValueError(
                "Pelvis interpoint must be expressable w.r.t. the center of mass in the"
                " pelvis frame.") from e
        self._pelvis_interpoint = value


class SideLeanSeatTorque(LoadGroupBase):
    """Torque load group for the side lean seat connection."""

    parent: SideLeanSeat
    required_parent_type = SideLeanSeat

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.symbols["T"]: f"Side lean torque of {self.parent}",
        }

    def _define_objects(self) -> None:
        """Define the objects."""
        self.symbols["T"] = dynamicsymbols(self._add_prefix("T"))

    def _define_loads(self) -> None:
        """Define the kinematics."""
        self.system.add_actuators(
            TorqueActuator(self.symbols["T"], self.parent.frame_lean_axis,
                           self.parent.pelvis.frame, self.parent.rear_frame.frame)
        )


class SideLeanSeatSpringDamper(LoadGroupBase):
    """Torque applied to the side lean connection as linear spring-damper."""

    parent: SideLeanSeat
    required_parent_type = SideLeanSeat

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.symbols["k"]: f"Side lean stiffness of {self.parent}",
            self.symbols["c"]: f"Side lean damping of {self.parent}",
            self.symbols["q_ref"]: f"Side lean reference angle of {self.parent}",
        }

    def _define_objects(self) -> None:
        """Define the objects."""
        self.symbols.update({
            "k": dynamicsymbols(self._add_prefix("k")),
            "c": dynamicsymbols(self._add_prefix("c")),
            "q_ref": dynamicsymbols(self._add_prefix("q_ref")),
        })

    def _define_loads(self) -> None:
        """Define the kinematics."""
        pin = self.parent.system.joints[0]
        self.system.add_actuators(
            TorqueActuator(
                -self.symbols["k"] * (pin.coordinates[0] - self.symbols["q_ref"]) -
                self.symbols["c"] * pin.speeds[0],
                self.parent.frame_lean_axis, self.parent.pelvis.frame,
                self.parent.rear_frame.frame)
        )
