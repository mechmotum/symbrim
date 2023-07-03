"""Module containing the hip joints."""
from __future__ import annotations

from typing import Any

from sympy import Matrix, cos, sin
from sympy.physics.mechanics import (
    PinJoint,
    SphericalJoint,
    Torque,
    dynamicsymbols,
)
from sympy.physics.mechanics._system import System

from brim.core import LoadGroupBase
from brim.rider.base_connections import LeftHipBase, RightHipBase

__all__ = ["SphericalLeftHip", "SphericalRightHip", "PinRightHip", "PinLeftHip",
           "SphericalHipTorque"]


class SphericalHipMixin:
    """Spherical joint between the pelvis and the leg."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.q[0]: "Flexion angle of the hip.",
            self.q[1]: "Adduction angle of the hip.",
            self.q[2]: "Rotation angle of the hip.",
            self.u[0]: "Flexion angular velocity of the hip.",
            self.u[1]: "Adduction angular velocity of the hip.",
            self.u[2]: "Rotation angular velocity of the hip.",
        }

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self.q = Matrix(
            dynamicsymbols(self._add_prefix("q_flexion, q_adduction, q_rotation")))
        self.u = Matrix(
            dynamicsymbols(self._add_prefix("u_flexion, u_adduction, u_rotation")))
        self._system = System.from_newtonian(self.pelvis.body)


class SphericalLeftHip(SphericalHipMixin, LeftHipBase):
    """Spherical joint between the pelvis and the left leg."""

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        self.system.add_joints(
            SphericalJoint(
                self._add_prefix("joint"), self.pelvis.body, self.leg.hip, self.q,
                self.u, self.pelvis.left_hip_point, self.leg.hip_interpoint,
                self.pelvis.frame, self.leg.hip_interframe, rot_type="BODY",
                amounts=(self.q[0], -self.q[1], self.q[2]), rot_order="YXZ")
        )


class SphericalRightHip(SphericalHipMixin, RightHipBase):
    """Spherical joint between the pelvis and the right leg."""

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        self.system.add_joints(
            SphericalJoint(
                self._add_prefix("joint"), self.pelvis.body, self.leg.hip, self.q,
                self.u, self.pelvis.right_hip_point, self.leg.hip_interpoint,
                self.pelvis.frame, self.leg.hip_interframe, rot_type="BODY",
                amounts=(self.q[0], self.q[1], self.q[2]), rot_order="YXZ")
        )


class PinHipMixin:
    """Pin joint between the pelvis and the leg."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.q: "Flexion angle of the hip.",
            self.u: "Flexion angular velocity of the hip.",
        }

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self.q = dynamicsymbols(self._add_prefix("q_flexion"))
        self.u = dynamicsymbols(self._add_prefix("u_flexion"))
        self._system = System.from_newtonian(self.pelvis.body)

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        self.system.add_joints(
            PinJoint(
                self._add_prefix("joint"), self.pelvis.body, self.leg.hip, self.q,
                self.u, self.pelvis.left_hip_point, self.leg.hip_interpoint,
                self.pelvis.frame, self.leg.hip_interframe,
                joint_axis=self.pelvis.y)
        )


class PinLeftHip(PinHipMixin, LeftHipBase):
    """Pin joint between the pelvis and the left leg."""


class PinRightHip(PinHipMixin, RightHipBase):
    """Pin joint between the pelvis and the right leg."""


class SphericalHipTorque(LoadGroupBase):
    """Torque actuator for the spherical hip joints."""

    parent: SphericalLeftHip | SphericalRightHip
    required_parent_type = (SphericalLeftHip, SphericalRightHip)

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.symbols["T_flexion"]: "Flexion torque of the hip.",
            self.symbols["T_adduction"]: "Adduction torque of the hip.",
            self.symbols["T_rotation"]: "Rotation torque of the hip.",
        }

    def _define_objects(self) -> None:
        """Define the objects."""
        self.symbols.update({name: dynamicsymbols(self._add_prefix(name)) for name in (
            "T_flexion", "T_adduction", "T_rotation")})

    def _define_loads(self) -> None:
        """Define the loads."""
        hip = self.parent.system.joints[0]
        adduction_axis = (cos(hip.coordinates[0]) * hip.parent_interframe.x -
                          sin(hip.coordinates[0]) * hip.parent_interframe.z)
        if isinstance(self.parent, LeftHipBase):
            adduction_axis *= -1
        torque = (self.symbols["T_flexion"] * hip.parent_interframe.y +
                  self.symbols["T_adduction"] * adduction_axis +
                  self.symbols["T_rotation"] * hip.child_interframe.z)
        self.parent.system.add_loads(
            Torque(hip.child_interframe, torque),
            Torque(hip.parent_interframe, -torque)
        )
