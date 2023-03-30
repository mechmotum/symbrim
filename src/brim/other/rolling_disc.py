"""Module containing the rolling disc model."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sympy import Matrix, Symbol, symbols
from sympy.physics.mechanics import (
    ReferenceFrame,
    RigidBody,
    System,
    cross,
    dynamicsymbols,
    inertia,
)

from brim.bicycle.grounds import GroundBase
from brim.bicycle.wheels import WheelBase
from brim.core import ModelBase, Requirement

if TYPE_CHECKING:
    pass


class RollingDisc(ModelBase):
    """Rolling disc model."""

    requirements: tuple[Requirement, ...] = (
        Requirement("ground", GroundBase, "Ground model."),
        Requirement("disc", WheelBase, "Disc model."),
    )
    ground: GroundBase
    disc: WheelBase

    @property
    def descriptions(self) -> dict[Any, str]:
        """Dictionary of descriptions of the rolling disc's attributes."""
        desc = {
            **super().descriptions,
            self.q[0]: "Perpendicular distance along ground.x to the contact point in "
                       "the ground plane.",
            self.q[1]: "Perpendicular distance along ground.y to the contact point in "
                       "the ground plane.",
            self.q[2]: "Yaw angle of the disc.",
            self.q[3]: "Roll angle of the disc.",
            self.q[4]: "Pitch angle of the disc.",
        }
        desc.update({ui: f"Generalized speed of the {desc[qi].lower()}"
                     for qi, ui in zip(self.q, self.u)})
        return desc

    def define_objects(self) -> None:
        """Define the objects of the rolling disc."""
        super().define_objects()
        self.q = Matrix([dynamicsymbols(self._add_prefix("q1:6"))])
        self.u = Matrix([dynamicsymbols(self._add_prefix("u1:6"))])

    def define_kinematics(self) -> None:
        """Define the kinematics of the rolling disc."""
        super().define_kinematics()
        self._system = System.from_newtonian(self.ground.body)
        self.disc.frame.orient_body_fixed(self.ground.frame, self.q[2:], "zxy")
        self.disc.frame.set_ang_vel(
            self.ground.frame, self.disc.frame.ang_vel_in(self.ground.frame).xreplace(
                {qi.diff(dynamicsymbols._t): ui for qi, ui in zip(self.q, self.u)}
            ))
        self.disc.contact_point.set_pos(
            self.ground.origin,
            self.q[0] * self.ground.planar_vectors[0] +
            self.q[1] * self.ground.planar_vectors[1]
        )
        self.disc.contact_point.set_vel(
            self.ground.frame,
            self.u[0] * self.ground.planar_vectors[0] +
            self.u[1] * self.ground.planar_vectors[1]
        )
        self.disc.compute_contact_point(self.ground)
        self.disc.compute_tyre_model(self.ground, True)
        self.system.q_ind = self.q
        self.system.u_ind = self.u
        self.system.kdes = [
            qdi - ui for qdi, ui in zip(self.q.diff(dynamicsymbols._t), self.u)]

    def define_loads(self) -> None:
        """Define the loads of the rolling disc."""
        super().define_loads()


def rolling_disc_manual() -> System:
    """Create a rolling disc model manually.

    Notes
    -----
    This function is used to verify and benchmark the rolling disc model. It is mostly
    copied from _create_rolling_disc in test_kane5.py from SymPy.
    """
    # Define symbols and coordinates
    t = dynamicsymbols._t
    q = dynamicsymbols("q1:6")
    u = dynamicsymbols("u1:6")
    qd_repl = {qi.diff(t): ui for qi, ui in zip(q, u)}
    # Define bodies and frames
    ground = RigidBody("ground")
    disc = RigidBody("disc", mass=Symbol("m"))
    disc.inertia = (inertia(disc.frame, *symbols("ixx iyy ixx")), disc.masscenter)
    ground.masscenter.set_vel(ground.frame, 0)
    disc.masscenter.set_vel(disc.frame, 0)
    int_frame = ReferenceFrame("int_frame")

    # Orient frames
    int_frame.orient_body_fixed(ground.frame, (q[2], q[3], 0), "zxy")
    disc.frame.orient_axis(int_frame, int_frame.y, q[4])
    g_w_d = disc.frame.ang_vel_in(ground.frame)
    disc.frame.set_ang_vel(ground.frame, g_w_d.xreplace(qd_repl))
    # Define points
    cp = ground.masscenter.locatenew("contact_point",
                                     q[0] * ground.x + q[1] * ground.y)
    cp.set_vel(ground.frame, u[0] * ground.x + u[1] * ground.y)
    disc.masscenter.set_pos(cp, -Symbol("r") * int_frame.z)

    # Define kinematic differential equations
    kdes = [qdi - ui for qdi, ui in qd_repl.items()]
    # Define nonholonomic constraints
    v0 = disc.masscenter.vel(ground.frame) + cross(
        disc.frame.ang_vel_in(ground.frame), cp.pos_from(disc.masscenter))
    fnh = [v0.dot(ground.x), v0.dot(ground.y)]
    # Create system
    system = System.from_newtonian(ground)
    system.q_ind = q
    system.u_ind = u[2:]
    system.u_dep = u[:2]
    system.kdes = kdes
    system.nonholonomic_constraints = fnh
    system.bodies = disc
    system.loads = [(disc.masscenter, disc.mass * Symbol("g") * ground.z)]
    return system
