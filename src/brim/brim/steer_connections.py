"""Module containing the steer connections."""
from __future__ import annotations

from sympy.physics.mechanics import dynamicsymbols
from sympy.physics.mechanics._system import System

from brim.brim.base_connections import SteerConnectionBase
from brim.utilities.utilities import check_zero

__all__ = ["HolonomicSteerConnection"]


class HolonomicSteerConnection(SteerConnectionBase):
    """Defines the connection between the hands and the steer as holonomic constraints.

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
