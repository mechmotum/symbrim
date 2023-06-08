"""Module containing the pedal connections."""
from __future__ import annotations

from sympy.physics.mechanics import dynamicsymbols
from sympy.physics.mechanics._system import System

from brim.brim.base_connections import PedalConnectionBase
from brim.utilities.utilities import random_eval

__all__ = ["HolonomicPedalsConnection"]


class HolonomicPedalsConnection(PedalConnectionBase):
    """Defines the connection between the hands and the steer as holonomic constraints.

    Explanation
    -----------
    This connection defines the feet as holonomic constraints on the pedals. The closed
    loop should be time independent in all directions, otherwise one will introduce
    additional constraints making the resulting system invalid. Some simple checks are
    done to verify that this is not the case. It is however that these will not catch
    the error. An example where this may occur is when the legs are purely two 2D and
    the distance between the pedals is different than the hip width.
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
                (self.left_leg.foot_interpoint, self.pedals.left_pedal_point),
                (self.right_leg.foot_interpoint, self.pedals.right_pedal_point)):
            for direction in self.pedals.frame:
                constr = fp.pos_from(pp).dot(direction)
                if random_eval(constr) != 0:
                    if random_eval(constr.diff(dynamicsymbols._t)) == 0:
                        error_msg.append(
                            f"While constraining the the feet to the pedals, it was "
                            f"found that the holonomic constraint of a foot along "
                            f"{direction} is not dependent on time. The following "
                            f"equations should be set to zero by redefining symbols "
                            f"before the define_kinematics stage: {constr}")
                    constrs.append(constr)
        if error_msg:
            raise ValueError(error_msg)
        self.system.add_holonomic_constraints(*constrs)
