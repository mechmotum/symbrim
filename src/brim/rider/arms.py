"""Module containing models of the arms."""
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from sympy import Symbol
from sympy.physics.mechanics import PinJoint, Point, RigidBody, dynamicsymbols, inertia
from sympy.physics.mechanics._system import System

from brim.core import ModelBase

if TYPE_CHECKING:
    from sympy.physics.mechanics import ReferenceFrame

__all__ = ["ArmBase", "LeftArmBase", "RightArmBase", "PinElbowStickLeftArm",
           "PinElbowStickRightArm"]


class ArmBase(ModelBase):
    """Base class for the arms of the rider."""

    def define_objects(self) -> None:
        """Define the objects."""
        super().define_objects()
        self._shoulder_interpoint = Point(self._add_prefix("SP"))
        self._hand_interpoint = Point(self._add_prefix("HP"))

    @property
    @abstractmethod
    def shoulder(self) -> RigidBody:
        """Shoulder of the arm."""

    @property
    def shoulder_interpoint(self) -> Point:
        """Point where the shoulder is attached to the torso."""
        return self._shoulder_interpoint

    @property
    @abstractmethod
    def shoulder_interframe(self) -> ReferenceFrame:
        """Frame to be used as inteframe between the shoulder and the torso."""

    @property
    @abstractmethod
    def hand(self) -> RigidBody:
        """Hand of the arm."""

    @property
    def hand_interpoint(self) -> Point:
        """Point where the hand is attached to the steer."""
        return self._hand_interpoint

    @property
    @abstractmethod
    def hand_interframe(self) -> ReferenceFrame:
        """Frame to be used as inteframe between the hand and the steer."""


class LeftArmBase(ArmBase):
    """Base class for the left arm of the rider."""


class RightArmBase(ArmBase):
    """Base class for the right arm of the rider."""


class PinElbowStickArmMixin:
    """Mixin class for arms with a pin elbow joint."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.symbols["l_upper_arm"]: "Upper arm length",
            self.symbols["l_upper_arm_com"]: "Upper arm center of mass position from "
                                             "shoulder.",
            self.symbols["l_forearm"]: "Forearm length",
            self.symbols["l_forearm_com"]: "Forearm center of mass position from "
                                           "elbow.",
            self.symbols["I_upper_arm"]: "Upper arm moment of inertia.",
            self.symbols["I_forearm"]: "Forearm moment of inertia.",
            self.q: "Elbow flexion angle",
            self.u: "Elbow flexion angular velocity",
        }

    def define_objects(self):
        """Define the objects."""
        super().define_objects()
        self.symbols.update({
            "l_upper_arm": Symbol(self._add_prefix("l_upper_arm")),
            "l_upper_arm_com": Symbol(self._add_prefix("l_upper_arm_com")),
            "l_forearm": Symbol(self._add_prefix("l_forearm")),
            "l_forearm_com": Symbol(self._add_prefix("l_forearm_com")),
            "I_upper_arm": Symbol(self._add_prefix("I_upper_arm")),
            "I_forearm": Symbol(self._add_prefix("I_forearm")),
        })
        self.q = dynamicsymbols(self._add_prefix("q_elbow_flexion"))
        self.u = dynamicsymbols(self._add_prefix("u_elbow_flexion"))
        self._upper_arm = RigidBody(self._add_prefix("upper_arm"))
        self.upper_arm.central_inertia = inertia(
            self.upper_arm.frame, self.symbols["I_upper_arm"],
            self.symbols["I_upper_arm"], 0)
        self._forearm = RigidBody(self._add_prefix("forearm"))
        self.forearm.central_inertia = inertia(
            self.forearm.frame, self.symbols["I_forearm"], self.symbols["I_forearm"], 0)
        self._system = System.from_newtonian(self.upper_arm)

    def define_kinematics(self) -> None:
        """Define the kinematics."""
        super().define_kinematics()
        l_u, l_f, l_uc, l_fc = (self.symbols[name] for name in (
            "l_upper_arm", "l_forearm", "l_upper_arm_com", "l_forearm_com"))
        self.upper_arm.masscenter.set_pos(
            self.shoulder_interpoint, l_uc * self.upper_arm.z)
        self.forearm.masscenter.set_pos(
            self.hand_interpoint, (l_fc - l_f) * self.forearm.z)
        self.system.add_joints(
            PinJoint(
                self._add_prefix("elbow"), self.upper_arm, self.forearm, self.q,
                self.u, (l_u - l_uc) * self.upper_arm.z, -l_fc * self.forearm.z,
                joint_axis=self.upper_arm.y)
        )

    @property
    def upper_arm(self) -> RigidBody:
        """Upper arm of the arm."""
        return self._upper_arm

    @property
    def forearm(self) -> RigidBody:
        """Forearm of the arm."""
        return self._forearm

    @property
    def shoulder(self) -> RigidBody:
        """Shoulder of the arm."""
        return self._upper_arm

    @property
    def hand(self) -> RigidBody:
        """Hand of the arm."""
        return self._forearm

    @property
    def shoulder_interframe(self) -> ReferenceFrame:
        """Frame to be used as inteframe between the shoulder and the torso."""
        return self.upper_arm.frame

    @property
    def hand_interframe(self) -> ReferenceFrame:
        """Frame to be used as inteframe between the hand and the steer."""
        return self.hand.frame


class PinElbowStickLeftArm(PinElbowStickArmMixin, LeftArmBase):
    """Left arm of the rider with a pin elbow joint."""


class PinElbowStickRightArm(PinElbowStickArmMixin, RightArmBase):
    """Right arm of the rider with a pin elbow joint."""
