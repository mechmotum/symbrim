"""Module containing the hand grip connections."""
from __future__ import annotations

from typing import Any

from sympy import symbols
from sympy.physics.mechanics import LinearPathway, dynamicsymbols
from sympy.physics.mechanics._actuator import LinearDamper, LinearSpring
from sympy.physics.mechanics._system import System

from brim.brim.base_connections import HandGripsBase
from brim.utilities.utilities import check_zero

__all__ = ["HolonomicHandGrips", "SpringDamperHandGrips"]


class HolonomicHandGrips(HandGripsBase):
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

        def attach_hand(hand_point, steer_point):
            """Attach the hand to the steer."""
            for direction in self.front_frame.frame:
                constr = hand_point.pos_from(steer_point).dot(direction)
                if not check_zero(constr):
                    if check_zero(constr.diff(dynamicsymbols._t)):
                        error_msg.append(
                            f"While constraining the the hands to the steer, it was "
                            f"found that the holonomic constraint of a hand along "
                            f"{direction} is not dependent on time. The following "
                            f"equations should be set to zero by redefining symbols "
                            f"before the define_kinematics stage: {constr}")
                    constrs.append(constr)

        super()._define_constraints()
        error_msg, constrs = [], []
        if self.left_arm:
            attach_hand(self.left_arm.hand_interpoint, self.front_frame.left_hand_grip)
        if self.right_arm:
            attach_hand(self.right_arm.hand_interpoint,
                        self.front_frame.right_hand_grip)
        if error_msg:
            raise ValueError(error_msg)
        self.system.add_holonomic_constraints(*constrs)


class SpringDamperHandGrips(HandGripsBase):
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
        if self.left_arm:
            path_left = LinearPathway(
                self.front_frame.left_hand_grip, self.left_arm.hand_interpoint)
            self.system.add_actuators(
                LinearSpring(self.symbols["k"], path_left),
                LinearDamper(self.symbols["c"], path_left)
            )
        if self.right_arm:
            path_right = LinearPathway(
                self.front_frame.right_hand_grip, self.right_arm.hand_interpoint)
            self.system.add_actuators(
                LinearSpring(self.symbols["k"], path_right),
                LinearDamper(self.symbols["c"], path_right)
            )
