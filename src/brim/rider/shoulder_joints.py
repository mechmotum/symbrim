"""Module containing the shoulder joints."""
from __future__ import annotations

from typing import Any

from sympy import Matrix
from sympy.physics.mechanics import SphericalJoint, dynamicsymbols
from sympy.physics.mechanics._system import System

from brim.rider.base_connections import LeftShoulderBase, RightShoulderBase

__all__ = ["SphericalLeftShoulder", "SphericalRightShoulder"]


class SphericalShoulderMixin:
    """Spherical joint between the pelvis and the leg."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.q[0]: "Flexion angle of the shoulder.",
            self.q[1]: "Adduction angle of the shoulder.",
            self.q[2]: "Rotation angle of the shoulder.",
            self.u[0]: "Flexion angular velocity of the shoulder.",
            self.u[1]: "Adduction angular velocity of the shoulder.",
            self.u[2]: "Rotation angular velocity of the shoulder.",
        }

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self.q = Matrix(
            dynamicsymbols(self._add_prefix("q_flexion, q_adduction, q_rotation")))
        self.u = Matrix(
            dynamicsymbols(self._add_prefix("u_flexion, u_adduction, u_rotation")))
        self._system = System.from_newtonian(self.torso.body)


class SphericalLeftShoulder(SphericalShoulderMixin, LeftShoulderBase):
    """Spherical joint between the pelvis and the left leg."""

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        self.system.add_joints(
            SphericalJoint(
                self._add_prefix("joint"), self.torso.body, self.arm.shoulder, self.q,
                self.u, self.torso.left_shoulder_point, self.arm.shoulder_interpoint,
                self.torso.left_shoulder_frame, self.arm.shoulder_interframe,
                rot_type="BODY", amounts=(self.q[0], -self.q[1], self.q[2]),
                rot_order="YXZ")
        )


class SphericalRightShoulder(SphericalShoulderMixin, RightShoulderBase):
    """Spherical joint between the pelvis and the right leg."""

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        self.system.add_joints(
            SphericalJoint(
                self._add_prefix("joint"), self.torso.body, self.arm.shoulder, self.q,
                self.u, self.torso.right_shoulder_point, self.arm.shoulder_interpoint,
                self.torso.right_shoulder_frame, self.arm.shoulder_interframe,
                rot_type="BODY", amounts=(self.q[0], self.q[1], self.q[2]),
                rot_order="YXZ")
        )
