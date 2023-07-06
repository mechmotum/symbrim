"""Module containing the steer connections."""
from __future__ import annotations

from typing import Any

from sympy import symbols
from sympy.physics.mechanics import dynamicsymbols
from sympy.physics.mechanics._actuator import LinearDamper, LinearSpring
from sympy.physics.mechanics._pathway import LinearPathway
from sympy.physics.mechanics._system import System

from brim.brim.base_connections import HandGripBase
from brim.utilities.utilities import check_zero

__all__ = ["HolonomicHandGrip", "SpringDamperHandGrip"]


class HolonomicHandGrip(HandGripBase):
    """Constrain the hands to the steer using holonomic constraints.

    Explanation
    -----------
    This connection defines the hands as holonomic constraints on the steer. The closed
    loop should be time independent in all directions, otherwise one will introduce
    additional constraints making the resulting system invalid. Some simple checks are
    done to verify that this is not the case. An example where this may occur is when
    the arms cannot move sideways with respect to the steer, while the shoulder width
    and the steer width are different.
    """

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self._system = System()

    def _define_constraints(self) -> None:
        """Define the constraints."""
        super()._define_constraints()
        error_msg, constrs = [], []
        for fp, pp in (
                (self.left_arm.hand_interpoint, self.steer.left_handgrip),
                (self.right_arm.hand_interpoint, self.steer.right_handgrip)):
            for direction in self.steer.frame:
                constr = fp.pos_from(pp).dot(direction)
                if not check_zero(constr):
                    if check_zero(constr.diff(dynamicsymbols._t)):
                        error_msg.append(
                            f"While constraining the the hands to the steer, it was "
                            f"found that the holonomic constraint of a hand along "
                            f"{direction} is not dependent on time. The following "
                            f"equations should be set to zero by redefining symbols "
                            f"before the define_kinematics stage: {constr}")
                    constrs.append(constr)
        if error_msg:
            raise ValueError(error_msg)
        self.system.add_holonomic_constraints(*constrs)


class SpringDamperHandGrip(HandGripBase):
    """Constrain the hands to the steer using spring-dampers."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.symbols["k"]:
                "Spring stiffness of the connection between the steer and the hands.",
            self.symbols["c"]: "Damping coefficient of the connection between the "
                               "steer and the hands.",
        }

    def _define_objects(self) -> None:
        """Define the objects."""
        self.symbols["k"], self.symbols["c"] = symbols(self._add_prefix("k c"))
        self._system = System()

    def _define_loads(self) -> None:
        """Define the loads."""
        super()._define_loads()
        path_left = LinearPathway(
            self.steer.left_handgrip, self.left_arm.hand_interpoint)
        path_right = LinearPathway(
            self.steer.right_handgrip, self.right_arm.hand_interpoint)
        self.system.add_actuators(
            LinearSpring(self.symbols["k"], path_left),
            LinearDamper(self.symbols["c"], path_left),
            LinearSpring(self.symbols["k"], path_right),
            LinearDamper(self.symbols["c"], path_right)
        )
