"""Module containing models of the legs."""
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from sympy import Matrix, Symbol
from sympy.physics.mechanics import PinJoint, Point, RigidBody, dynamicsymbols, inertia
from sympy.physics.mechanics._system import System

from brim.core import ModelBase

if TYPE_CHECKING:
    from sympy.physics.mechanics import ReferenceFrame

__all__ = ["LegBase", "LeftLegBase", "RightLegBase", "TwoPinStickLeftLeg",
           "TwoPinStickRightLeg"]


class LegBase(ModelBase):
    """Base class for the leg of the rider."""

    def define_objects(self) -> None:
        """Define the objects."""
        super().define_objects()
        self._hip_interpoint = Point(self._add_prefix("HP"))
        self._foot_interpoint = Point(self._add_prefix("FP"))

    def define_kinematics(self) -> None:
        """Define the kinematics."""
        self.hip_interpoint.set_vel(self.hip_interframe, 0)
        self.foot_interpoint.set_vel(self.foot_interframe, 0)

    @property
    @abstractmethod
    def hip(self) -> RigidBody:
        """Hip of the leg."""

    @property
    def hip_interpoint(self) -> Point:
        """Point where the hip is attached to the pelvis."""
        return self._hip_interpoint

    @property
    @abstractmethod
    def hip_interframe(self) -> ReferenceFrame:
        """Frame to be used as inteframe between the hip and the pelvis."""

    @property
    @abstractmethod
    def foot(self) -> RigidBody:
        """Foot of the leg."""

    @property
    def foot_interpoint(self) -> Point:
        """Point where the foot is attached to the pedals."""
        return self._foot_interpoint

    @property
    @abstractmethod
    def foot_interframe(self) -> ReferenceFrame:
        """Frame to be used as inteframe between the foot and the pedals."""


class LeftLegBase(LegBase):
    """Base class for the left leg of the rider."""


class RightLegBase(LegBase):
    """Base class for the right leg of the rider."""


class TwoPinStickLegMixin:
    """Mixin class for a leg with two pin joints."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.symbols["l_thigh"]: "Length of the thigh.",
            self.symbols["l_thigh_com"]: "Distance from the hip joint to the center of "
                                         "mass of the thigh.",
            self.symbols["l_shank"]: "Length of the shank.",
            self.symbols["l_shank_com"]: "Distance from the knee joint to the center of"
                                         " mass of the shank.",
            self.symbols["l_foot"]: "Length of the foot.",
            self.symbols["l_foot_com"]: "Distance from the ankle joint to the center of"
                                        " mass of the foot.",
            self.symbols["I_thigh"]: "Moment of inertia of the thigh around its "
                                     "center of mass.",
            self.symbols["I_shank"]: "Moment of inertia of the shank around its "
                                     "center of mass.",
            self.symbols["I_foot"]: "Moment of inertia of the foot around its "
                                    "center of mass.",
        }

    def define_objects(self) -> None:
        """Define the objects."""
        super().define_objects()
        self.symbols.update({
            "l_thigh": Symbol(self._add_prefix("l_thigh")),
            "l_thigh_com": Symbol(self._add_prefix("l_thigh_com")),
            "l_shank": Symbol(self._add_prefix("l_shank")),
            "l_shank_com": Symbol(self._add_prefix("l_shank_com")),
            "l_foot": Symbol(self._add_prefix("l_foot")),
            "l_foot_com": Symbol(self._add_prefix("l_foot_com")),
            "I_thigh": Symbol(self._add_prefix("I_thigh")),
            "I_shank": Symbol(self._add_prefix("I_shank")),
            "I_foot": Symbol(self._add_prefix("I_foot")),
        })
        self.q = Matrix(
            dynamicsymbols(self._add_prefix("q_knee_flexion q_ankle_flexion")))
        self.u = Matrix(
            dynamicsymbols(self._add_prefix("u_knee_flexion u_ankle_flexion")))
        self._thigh = RigidBody(self._add_prefix("thigh"))
        self.thigh.central_inertia = inertia(
            self.thigh.frame, self.symbols["I_thigh"], self.symbols["I_thigh"], 0)
        self._shank = RigidBody(self._add_prefix("shank"))
        self.shank.central_inertia = inertia(
            self.shank.frame, self.symbols["I_shank"], self.symbols["I_shank"], 0)
        self._foot = RigidBody(self._add_prefix("foot"))
        self.foot.central_inertia = inertia(
            self.foot.frame, 0, self.symbols["I_foot"], self.symbols["I_foot"])
        self._system = System.from_newtonian(self.hip)

    def define_kinematics(self) -> None:
        """Define the kinematics."""
        super().define_kinematics()
        l_f, l_t, l_s, l_f_com, l_t_com, l_s_com = (self.symbols[length] for length in (
            "l_foot", "l_thigh", "l_shank", "l_foot_com", "l_thigh_com", "l_shank_com"))
        self.hip.masscenter.set_pos(self.hip_interpoint, l_t_com * self.thigh.z)
        self.foot.masscenter.set_pos(self.foot_interpoint,
                                     (l_f_com - l_f) * self.foot.x)
        self.system.add_joints(
            PinJoint(
                self._add_prefix("knee"), self.thigh, self.shank, self.q[0], self.u[0],
                (l_t - l_t_com) * self.thigh.z, -l_s_com * self.shank.z,
                joint_axis=-self.thigh.y),
            PinJoint(
                self._add_prefix("ankle"), self.shank, self.foot, self.q[1], self.u[1],
                (l_s - l_s_com) * self.shank.z, -l_f_com * self.foot.x,
                joint_axis=-self.shank.y),
        )

    @property
    def hip(self) -> RigidBody:
        """Hip of the leg."""
        return self._thigh

    @property
    def hip_interframe(self) -> ReferenceFrame:
        """Frame to be used as inteframe between the hip and the pelvis."""
        return self._thigh.frame

    @property
    def foot_interframe(self) -> ReferenceFrame:
        """Frame to be used as inteframe between the foot and the pedals."""
        return self._foot.frame

    @property
    def thigh(self) -> RigidBody:
        """Thigh of the leg."""
        return self._thigh

    @property
    def shank(self) -> RigidBody:
        """Shank of the leg."""
        return self._shank

    @property
    def foot(self) -> RigidBody:
        """Foot of the leg."""
        return self._foot


class TwoPinStickLeftLeg(TwoPinStickLegMixin, LeftLegBase):
    """Left leg of the rider with two pin joints."""


class TwoPinStickRightLeg(TwoPinStickLegMixin, RightLegBase):
    """Right leg of the rider with two pin joints."""
