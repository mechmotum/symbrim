import itertools

from brim.bicycle import FlatGround, KnifeEdgeWheel, NonHolonomicTyre
from brim.other.rolling_disc import RollingDisc
from brim.utilities.benchmarking import benchmark
from sympy import count_ops, cse, symbols
from sympy.physics.mechanics import (
    KanesMethod,
    Point,
    ReferenceFrame,
    RigidBody,
    cross,
    dot,
    dynamicsymbols,
    inertia,
)


def rolling_disc_from_sympy_test_suite():
    # This is the rolling disc example from the test_kane.py file in the
    # sympy.physics.mechanics module. The difference of this example compared to the
    # others is that it only uses 3 generalized coordinates and speeds.
    # Rolling Disc Example
    # Here the rolling disc is formed from the contact point up, removing the
    # need to introduce generalized speeds. Only 3 configuration and three
    # speed variables are need to describe this system, along with the disc's
    # mass and radius, and the local gravity (note that mass will drop out).
    q1, q2, q3, u1, u2, u3 = dynamicsymbols("q1 q2 q3 u1 u2 u3")
    q1d, q2d, q3d, u1d, u2d, u3d = dynamicsymbols("q1 q2 q3 u1 u2 u3", 1)
    r, m, g = symbols("r m g")

    # The kinematics are formed by a series of simple rotations. Each simple
    # rotation creates a new frame, and the next rotation is defined by the new
    # frame's basis vectors. This example uses a 3-1-2 series of rotations, or
    # Z, X, Y series of rotations. Angular velocity for this is defined using
    # the second frame's basis (the lean frame).
    N = ReferenceFrame("N")  # noqa: N806
    Y = N.orientnew("Y", "Axis", [q1, N.z])  # noqa: N806
    L = Y.orientnew("L", "Axis", [q2, Y.x])  # noqa: N806
    R = L.orientnew("R", "Axis", [q3, L.y])  # noqa: N806
    w_R_N_qd = R.ang_vel_in(N)  # noqa: N806
    R.set_ang_vel(N, u1 * L.x + u2 * L.y + u3 * L.z)

    # This is the translational kinematics. We create a point with no velocity
    # in N; this is the contact point between the disc and ground. Next we form
    # the position vector from the contact point to the disc's center of mass.
    # Finally we form the velocity and acceleration of the disc.
    C = Point("C")  # noqa: N806
    C.set_vel(N, 0)
    Dmc = C.locatenew("Dmc", r * L.z)  # noqa: N806
    Dmc.v2pt_theory(C, N, R)

    # This is a simple way to form the inertia dyadic.
    I = inertia(L, m / 4 * r ** 2, m / 2 * r ** 2, m / 4 * r ** 2)  # noqa: N806 E741

    # Kinematic differential equations; how the generalized coordinate time
    # derivatives relate to generalized speeds.
    kd = [dot(R.ang_vel_in(N) - w_R_N_qd, uv) for uv in L]

    # Creation of the force list; it is the gravitational force at the mass
    # center of the disc. Then we create the disc by assigning a Point to the
    # center of mass attribute, a ReferenceFrame to the frame attribute, and mass
    # and inertia. Then we form the body list.
    ForceList = [(Dmc, - m * g * Y.z)]  # noqa: N806
    BodyD = RigidBody("BodyD", Dmc, R, m, (I, Dmc))  # noqa: N806
    BodyList = [BodyD]  # noqa: N806

    # Finally we form the equations of motion, using the same steps we did
    # before. Specify inertial frame, supply generalized speeds, supply
    # kinematic differential equation dictionary, compute Fr from the force
    # list and Fr* from the body list, compute the mass matrix and forcing
    # terms, then solve for the u dots (time derivatives of the generalized
    # speeds).
    return KanesMethod(N, q_ind=[q1, q2, q3], u_ind=[u1, u2, u3], kd_eqs=kd,
                       bodies=BodyList, forcelist=ForceList)


def create_rolling_disc(efficient_kdes: bool, efficient_constraints: bool,
                        efficient_disc_velocity: bool, efficient_position: bool):
    t = dynamicsymbols._t
    q1, q2, q3, q4, q5, u1, u2, u3, u4, u5 = dynamicsymbols("q1:6 u1:6")
    g, r, m = symbols("g r m")
    # Define bodies and frames
    ground = RigidBody("ground")
    disc = RigidBody("disk", mass=m)
    disc.inertia = (inertia(disc.frame, *symbols("Ixx Iyy Ixx")), disc.masscenter)
    ground.masscenter.set_vel(ground.frame, 0)
    disc.masscenter.set_vel(disc.frame, 0)
    int_frame = ReferenceFrame("int_frame")
    # Orient frames
    int_frame.orient_body_fixed(ground.frame, (q1, q2, 0), "zxy")
    disc.frame.orient_axis(int_frame, int_frame.y, q3)
    g_w_d = disc.frame.ang_vel_in(ground.frame)
    if efficient_kdes:
        disc.frame.set_ang_vel(ground.frame, u1 * disc.x + u2 * disc.y + u3 * disc.z)
    # Define points
    cp = ground.masscenter.locatenew("contact_point", q4 * ground.x + q5 * ground.y)
    cp.set_vel(ground.frame, u4 * ground.x + u5 * ground.y)
    if efficient_position:
        disc.masscenter.set_pos(cp, -r * int_frame.z)
    else:
        disc.masscenter.set_pos(cp,
                                r * cross(disc.y, cross(disc.y, ground.z)).normalize())
    # Define kinematic differential equations
    if efficient_kdes:
        kdes = [g_w_d.dot(disc.x) - u1, g_w_d.dot(disc.y) - u2,
                g_w_d.dot(disc.z) - u3, q4.diff(t) - u4, q5.diff(t) - u5]
    else:
        kdes = [qi.diff(t) - ui for qi, ui in
                zip([q1, q2, q3, q4, q5], [u1, u2, u3, u4, u5])]

    # Define nonholonomic constraints
    if efficient_constraints:
        v_mc = disc.masscenter.vel(ground.frame)
        disc.masscenter.set_vel(ground.frame, cross(
            disc.frame.ang_vel_in(ground.frame), disc.masscenter.pos_from(cp)))
        v0 = cp.vel(ground.frame) + cross(
            disc.frame.ang_vel_in(int_frame), cp.pos_from(disc.masscenter))
        disc.masscenter.set_vel(ground.frame, v_mc)
    else:
        v0 = disc.masscenter.vel(ground.frame) + cross(
            disc.frame.ang_vel_in(ground.frame),
            cp.pos_from(disc.masscenter)
        )
    if efficient_disc_velocity:
        disc.masscenter.set_vel(ground.frame, cross(
            disc.frame.ang_vel_in(ground.frame), disc.masscenter.pos_from(cp)))
    fnh = [v0.dot(ground.x), v0.dot(ground.y)]
    # Define loads
    loads = [(disc.masscenter, disc.mass * g * ground.z)]
    bodies = [disc]

    return KanesMethod(ground.frame, q_ind=[q1, q2, q3, q4, q5],
                       u_ind=[u1, u2, u3], kd_eqs=kdes,
                       velocity_constraints=fnh, u_dependent=[u4, u5],
                       bodies=bodies, forcelist=loads, explicit_kinematics=False)


def rolling_disc_comparison():
    settings = itertools.product((True, False), repeat=4)
    print("efficient_kdes\tefficient_constraints\tefficient_disc_velocity"  # noqa: T201
          "\tefficient_position\t#ops EoMs\t#ops CSEd EoMs")
    for setting in settings:
        kane = create_rolling_disc(*setting)
        eoms = kane._form_eoms()
        print("\t\t\t".join(map(str, setting)) +  # noqa: T201
              f"\t\t{count_ops(eoms)}\t\t{count_ops(cse(eoms))}")


@benchmark(rounds=10, group="rolling_disc")
def test_rolling_disc_efficient():
    return create_rolling_disc(True, True, True, True)


@benchmark(rounds=10, group="rolling_disc")
def test_rolling_disc_only_efficient_pos():
    return create_rolling_disc(False, False, False, True)


@benchmark(rounds=10, group="rolling_disc")
def test_rolling_disc_inefficient():
    return create_rolling_disc(False, False, False, False)


@benchmark(rounds=10, group="rolling_disc")
def test_rolling_disc_3_coords():
    return rolling_disc_from_sympy_test_suite()


@benchmark(rounds=10, group="rolling_disc")
def test_rolling_disc_brim():
    rolling_disc = RollingDisc("disc")
    rolling_disc.disc = KnifeEdgeWheel("wheel")
    rolling_disc.ground = FlatGround("ground")
    rolling_disc.tyre = NonHolonomicTyre("tyre")
    rolling_disc.define_all()
    system = rolling_disc.to_system()
    system.u_ind = rolling_disc.u[2:]
    system.u_dep = rolling_disc.u[:2]
    return system


if __name__ == "__main__":
    rolling_disc_comparison()
