"""Module containing models of the arms."""
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from sympy import Symbol
from sympy.physics.mechanics import PinJoint, Point, RigidBody, dynamicsymbols
from sympy.physics.mechanics._actuator import TorqueActuator
from sympy.physics.mechanics._system import System

from brim.core import LoadGroupBase, ModelBase

try:  # pragma: no cover
    from brim.utilities.parametrize import get_inertia_vals_from_yeadon

    if TYPE_CHECKING:
        from bicycleparameters import Bicycle
except ImportError:  # pragma: no cover
    pass

if TYPE_CHECKING:
    from sympy.physics.mechanics import ReferenceFrame

__all__ = ["ArmBase", "LeftArmBase", "RightArmBase", "PinElbowStickLeftArm",
           "PinElbowStickRightArm", "PinElbowStickArmTorque"]


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
        })
        self.q = dynamicsymbols(self._add_prefix("q_elbow_flexion"))
        self.u = dynamicsymbols(self._add_prefix("u_elbow_flexion"))
        self._upper_arm = RigidBody(self._add_prefix("upper_arm"))
        self._forearm = RigidBody(self._add_prefix("forearm"))
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

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get the parameter values of the pelvis."""
        params = super().get_param_values(bicycle_parameters)
        human = bicycle_parameters.human
        if human is None:
            return params
        params[self.upper_arm.mass] = human.A1.mass
        params[self.forearm.mass] = human.A2.mass
        params.update(
            get_inertia_vals_from_yeadon(self.upper_arm, human.A1.rel_inertia))
        params.update(get_inertia_vals_from_yeadon(self.forearm, human.A2.rel_inertia))
        params.update({
            self.symbols["l_upper_arm"]: human.meas["La2L"],
            self.symbols["l_forearm"]:
                human.meas["La5L"] + human.meas["La4L"] - human.meas["La2L"],
            self.symbols["l_upper_arm_com"]: -human.A1.rel_center_of_mass[2, 0],
            self.symbols["l_forearm_com"]: -human.A2.rel_center_of_mass[2, 0],
        })
        return params


class PinElbowStickRightArm(PinElbowStickArmMixin, RightArmBase):
    """Right arm of the rider with a pin elbow joint."""

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get the parameter values of the pelvis."""
        params = super().get_param_values(bicycle_parameters)
        human = bicycle_parameters.human
        if human is None:
            return params
        params[self.upper_arm.mass] = human.B1.mass
        params[self.forearm.mass] = human.B2.mass
        params.update(
            get_inertia_vals_from_yeadon(self.upper_arm, human.B1.rel_inertia))
        params.update(get_inertia_vals_from_yeadon(self.forearm, human.B2.rel_inertia))
        params.update({
            self.symbols["l_upper_arm"]: human.meas["Lb2L"],
            self.symbols["l_forearm"]:
                human.meas["Lb5L"] + human.meas["Lb4L"] - human.meas["Lb2L"],
            self.symbols["l_upper_arm_com"]: -human.B1.rel_center_of_mass[2, 0],
            self.symbols["l_forearm_com"]: -human.B2.rel_center_of_mass[2, 0],
        })
        return params


class PinElbowStickArmTorque(LoadGroupBase):
    """Torque applied to the elbow of the rider."""

    parent: PinElbowStickArmMixin

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            self.symbols["T_elbow"]: f"Elbow torque of {self.parent}",
        }

    def define_objects(self) -> None:
        """Define the objects."""
        self.symbols["T_elbow"] = dynamicsymbols(self._add_prefix("T_elbow"))

    def define_loads(self) -> None:
        """Define the kinematics."""
        self.system.add_actuators(
            TorqueActuator(self.symbols["T_elbow"], self.parent.upper_arm.y,
                           self.parent.forearm, self.parent.upper_arm)
        )
