"""Module containing the pedal connections."""
from __future__ import annotations

from sympy import symbols
from sympy.physics.mechanics import (
    LinearDamper,
    LinearPathway,
    LinearSpring,
    Point,
    System,
    dynamicsymbols,
)

from brim.brim.base_connections import PedalsBase
from brim.utilities.utilities import check_zero

__all__ = ["HolonomicPedals", "SpringDamperPedals"]


class HolonomicPedals(PedalsBase):
    """Constrain the feet to the pedals using holonomic constraints.

    Explanation
    -----------
    This connection defines the feet as holonomic constraints on the pedals. The closed
    loop should be time independent in all directions, otherwise one will introduce
    additional constraints making the resulting system invalid. Some simple checks are
    done to verify that this is not the case. It is however that these will not catch
    the error. An example where this may occur is when the legs are purely two 2D and
    the distance between the pedals is different from the hip width.
    """

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self._system = System(self.cranks.system.frame, self.cranks.system.fixed_point)

    def _define_constraints(self) -> None:
        """Define the constraints."""

        def attach_foot(foot_point: Point, pedal_point: Point) -> None:
            """Attach the foot to the pedal."""
            for direction in self.cranks.frame:
                constr = foot_point.pos_from(pedal_point).dot(direction)
                if not check_zero(constr):
                    if check_zero(constr.diff(dynamicsymbols._t)):
                        error_msg.append(
                            f"While constraining the the feet to the pedals, it was "
                            f"found that the holonomic constraint of a foot along "
                            f"{direction} is not dependent on time. The following "
                            f"equations should be set to zero by redefining symbols "
                            f"before the define_kinematics stage: {constr}")
                    hol_constrs.append(constr)
                    aux_vel = (
                        self.auxiliary_handler.get_auxiliary_velocity(foot_point) -
                        self.auxiliary_handler.get_auxiliary_velocity(pedal_point))
                    vel_constrs.append(constr.diff(dynamicsymbols._t) +
                                       aux_vel.dot(direction))

        super()._define_constraints()
        error_msg, hol_constrs, vel_constrs = [], [], []
        if self.left_leg:
            attach_foot(self.left_leg.foot_interpoint, self.cranks.left_pedal_point)
        if self.right_leg:
            attach_foot(self.right_leg.foot_interpoint, self.cranks.right_pedal_point)
        if error_msg:
            raise ValueError(error_msg)
        self.system.add_holonomic_constraints(*hol_constrs)
        self.system.velocity_constraints = vel_constrs


class SpringDamperPedals(PedalsBase):
    """Constrain the feet to the pedals using spring-damper."""

    @property
    def descriptions(self) -> dict[object, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.symbols["k"]:
                "Spring stiffness of the connection between the pedals and the feet.",
            self.symbols["c"]: "Damping coefficient of the connection between the "
                               "pedals and the feet.",
        }

    def _define_objects(self) -> None:
        """Define the objects."""
        self.symbols["k"], self.symbols["c"] = symbols(self._add_prefix("k c"))
        self._system = System()

    def _define_loads(self) -> None:
        """Define the loads."""
        super()._define_loads()
        if self.left_leg:
            path_left = LinearPathway(
                self.cranks.left_pedal_point, self.left_leg.foot_interpoint)
            self.system.add_actuators(
                LinearSpring(self.symbols["k"], path_left),
                LinearDamper(self.symbols["c"], path_left)
            )
        if self.right_leg:
            path_right = LinearPathway(
                self.cranks.right_pedal_point, self.right_leg.foot_interpoint)
            self.system.add_actuators(
                LinearSpring(self.symbols["k"], path_right),
                LinearDamper(self.symbols["c"], path_right)
            )
