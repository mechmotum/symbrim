"""Module containing the hip joints."""
from __future__ import annotations

from typing import Any

from sympy import Matrix
from sympy.physics.mechanics import PinJoint, SphericalJoint, dynamicsymbols
from sympy.physics.mechanics._system import System

from brim.rider.base_connections import LeftHipBase, RightHipBase

__all__ = ["SphericalLeftHip", "SphericalRightHip", "PinRightHip", "PinLeftHip"]


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

    def define_objects(self) -> None:
        """Define the objects."""
        super().define_objects()
        self.q = Matrix(
            dynamicsymbols(self._add_prefix("q_flexion, q_adduction, q_rotation")))
        self.u = Matrix(
            dynamicsymbols(self._add_prefix("u_flexion, u_adduction, u_rotation")))
        self._system = System.from_newtonian(self.pelvis.body)


class SphericalLeftHip(SphericalHipMixin, LeftHipBase):
    """Spherical joint between the pelvis and the left leg."""

    def define_kinematics(self) -> None:
        """Define the kinematics."""
        super().define_kinematics()
        self.system.add_joints(
            SphericalJoint(
                self._add_prefix("joint"), self.pelvis.body, self.leg.hip, self.q,
                self.u, self.pelvis.left_hip_point, self.leg.hip_interpoint,
                self.pelvis.frame, self.leg.hip_interframe, rot_type="BODY",
                amounts=(self.q[0], -self.q[1], self.q[2]), rot_order="YXZ")
        )


class SphericalRightHip(SphericalHipMixin, RightHipBase):
    """Spherical joint between the pelvis and the right leg."""

    def define_kinematics(self) -> None:
        """Define the kinematics."""
        super().define_kinematics()
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

    def define_objects(self) -> None:
        """Define the objects."""
        super().define_objects()
        self.q = dynamicsymbols(self._add_prefix("q_flexion"))
        self.u = dynamicsymbols(self._add_prefix("u_flexion"))
        self._system = System.from_newtonian(self.pelvis.body)


class PinLeftHip(PinHipMixin, LeftHipBase):
    """Pin joint between the pelvis and the left leg."""

    def define_kinematics(self) -> None:
        """Define the kinematics."""
        super().define_kinematics()
        self.system.add_joints(
            PinJoint(
                self._add_prefix("joint"), self.pelvis.body, self.leg.hip, self.q,
                self.u, self.pelvis.left_hip_point, self.leg.hip_interpoint,
                self.pelvis.frame, self.leg.hip_interframe,
                joint_axis=self.pelvis.y)
        )


class PinRightHip(PinHipMixin, RightHipBase):
    """Pin joint between the pelvis and the right leg."""

    def define_kinematics(self) -> None:
        """Define the kinematics."""
        super().define_kinematics()
        self.system.add_joints(
            PinJoint(
                self._add_prefix("joint"), self.pelvis.body, self.leg.hip, self.q,
                self.u, self.pelvis.right_hip_point, self.leg.hip_interpoint,
                self.pelvis.frame, self.leg.hip_interframe,
                joint_axis=self.pelvis.y)
        )
