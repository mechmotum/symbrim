from sympy import symbols
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

from brim.bicycle import (
    FlatGround,
    KnifeEdgeWheel,
    NonHolonomicTire,
    RigidFrontFrame,
    RigidRearFrame,
    WhippleBicycleMoore,
)
from brim.utilities.benchmarking import benchmark

ROUNDS = 3


def create_whipple_bicycle_moore_brim():
    bike = WhippleBicycleMoore("bike")
    bike.ground = FlatGround("ground")
    bike.rear_frame = RigidRearFrame("rear_frame")
    bike.front_frame = RigidFrontFrame("front_frame")
    bike.rear_wheel = KnifeEdgeWheel("rear_wheel")
    bike.front_wheel = KnifeEdgeWheel("front_wheel")
    bike.rear_tire = NonHolonomicTire("rear_tire")
    bike.front_tire = NonHolonomicTire("front_tire")
    bike.define_all()
    system = bike.to_system()
    system.apply_uniform_gravity(
        -symbols("g") * bike.ground.get_normal(bike.ground.origin))
    system.q_ind = [*bike.q[:4], *bike.q[5:]]
    system.q_dep = [bike.q[4]]
    system.u_ind = [bike.u[3], *bike.u[5:7]]
    system.u_dep = [*bike.u[:3], bike.u[4], bike.u[7]]
    return system


def create_whipple_bicycle_moore_minimal_coords():  # noqa: PLR0915
    N, A, B, C, D, E, F = symbols("N A:F", cls=ReferenceFrame)  # noqa: N806
    q1, q2, q3, q4 = dynamicsymbols("q1 q2 q3 q4")
    q5, q6, q7, q8 = dynamicsymbols("q5 q6 q7 q8")

    u1, u2, u3, u4 = dynamicsymbols("u1 u2 u3 u4")
    u5, u6, u7, u8 = dynamicsymbols("u5 u6 u7 u8")

    # rear frame yaw
    A.orient(N, "Axis", (q3, N.z))
    # rear frame roll
    B.orient(A, "Axis", (q4, A.x))
    # rear frame pitch
    C.orient(B, "Axis", (q5, B.y))
    # front frame steer
    E.orient(C, "Axis", (q7, C.z))

    rf, rr = symbols("rf rr")
    d1, d2, d3 = symbols("d1 d2 d3")
    l1, l2, l3, l4 = symbols("l1 l2 l3 l4")

    # acceleration due to gravity
    g = symbols("g")

    # mass
    mc, md, me, mf = symbols("mc md me mf")

    # inertia
    ic11, ic22, ic33, ic31 = symbols("ic11 ic22 ic33 ic31")
    id11, id22 = symbols("id11 id22")
    ie11, ie22, ie33, ie31 = symbols("ie11 ie22 ie33 ie31")
    if11, if22 = symbols("if11 if22")

    # rear wheel contact point
    dn = Point("dn")

    # rear wheel contact point to rear wheel center
    do = Point("do")
    do.set_pos(dn, -rr * B.z)

    # rear wheel center to bicycle frame center
    co = Point("co")
    co.set_pos(do, l1 * C.x + l2 * C.z)

    # rear wheel center to steer axis point
    ce = Point("ce")
    ce.set_pos(do, d1 * C.x)

    # steer axis point to the front wheel center
    fo = Point("fo")
    fo.set_pos(ce, d2 * E.z + d3 * E.x)

    # front wheel center to front frame center
    eo = Point("eo")
    eo.set_pos(fo, l3 * E.x + l4 * E.z)

    # locate the point fixed on the wheel which instantaneously touches the
    # ground
    fn = Point("fn")
    fn.set_pos(fo, rf * E.y.cross(A.z).cross(E.y).normalize())

    holonomic = fn.pos_from(dn).dot(A.z)

    t = dynamicsymbols._t

    kinematical = [q3.diff(t) - u3,  # yaw
                   q4.diff(t) - u4,  # roll
                   q5.diff(t) - u5,  # pitch
                   q7.diff(t) - u7]  # steer

    A.set_ang_vel(N, u3 * N.z)  # yaw rate
    B.set_ang_vel(A, u4 * A.x)  # roll rate
    C.set_ang_vel(B, u5 * B.y)  # pitch rate
    D.set_ang_vel(C, u6 * C.y)  # rear wheel rate
    E.set_ang_vel(C, u7 * C.z)  # steer rate
    F.set_ang_vel(E, u8 * E.y)  # front wheel rate

    # rear wheel contact stays in ground plane and does not slip
    dn.set_vel(N, 0.0 * N.x)

    # mass centers
    do.v2pt_theory(dn, N, D)
    co.v2pt_theory(do, N, C)
    ce.v2pt_theory(do, N, C)
    fo.v2pt_theory(ce, N, E)
    eo.v2pt_theory(fo, N, E)

    # wheel contact velocities
    fn.v2pt_theory(fo, N, F)  # supress output

    nonholonomic = [
        fn.vel(N).dot(A.x),
        fn.vel(N).dot(A.z),
        fn.vel(N).dot(A.y),
    ]

    Ic = inertia(C, ic11, ic22, ic33, 0, 0, ic31)  # noqa: N806
    Id = inertia(C, id11, id22, id11, 0, 0, 0)  # noqa: N806
    Ie = inertia(E, ie11, ie22, ie33, 0, 0, ie31)  # noqa: N806
    If = inertia(E, if11, if22, if11, 0, 0, 0)  # noqa: N806

    rear_frame = RigidBody("Rear Frame", co, C, mc, (Ic, co))
    rear_wheel = RigidBody("Rear Wheel", do, D, md, (Id, do))
    front_frame = RigidBody("Front Frame", eo, E, me, (Ie, eo))
    front_wheel = RigidBody("Front Wheel", fo, F, mf, (If, fo))

    bodies = [rear_frame, rear_wheel, front_frame, front_wheel]

    Fco = (co, mc * g * A.z)  # noqa: N806
    Fdo = (do, md * g * A.z)  # noqa: N806
    Feo = (eo, me * g * A.z)  # noqa: N806
    Ffo = (fo, mf * g * A.z)  # noqa: N806

    loads = [Fco, Fdo, Feo, Ffo]

    return KanesMethod(N,
                       [q3, q4, q7],  # yaw, roll, steer
                       [u4, u6, u7],  # roll rate, rear wheel rate, steer rate
                       kd_eqs=kinematical,
                       q_dependent=[q5],  # pitch angle
                       configuration_constraints=[holonomic],
                       u_dependent=[u3, u5, u8],
                       # yaw rate, pitch rate, front wheel rate
                       velocity_constraints=nonholonomic,
                       bodies=bodies, forcelist=loads, constraint_solver="CRAMER")


def create_whipple_bicycle_moore_full_coords():
    # Define symbols
    t = dynamicsymbols._t
    rf, rr = symbols("rf rr")
    d1, d2, d3 = symbols("d1 d2 d3")
    l1, l2, l3, l4 = symbols("l1 l2 l3 l4")
    g = symbols("g")
    mc, md, me, mf = symbols("mc md me mf")
    ic11, ic22, ic33, ic31 = symbols("ic11 ic22 ic33 ic31")
    id11, id22 = symbols("id11 id22")
    ie11, ie22, ie33, ie31 = symbols("ie11 ie22 ie33 ie31")
    if11, if22 = symbols("if11 if22")

    q1, q2, q3, q4, q5, q6, q7, q8 = dynamicsymbols("q1:9")
    u1, u2, u3, u4, u5, u6, u7, u8 = dynamicsymbols("u1:9")

    # Define frames
    N, A, B, C, D, E, F = symbols("N A:F", cls=ReferenceFrame)  # noqa: N806
    A.orient_axis(N, N.z, q3)  # rear frame yaw
    B.orient_axis(A, A.x, q4)  # rear frame roll
    C.orient_axis(B, B.y, q5)  # rear frame pitch
    E.orient_axis(C, C.z, q7)  # front frame steer
    D.orient_axis(C, C.y, q6)  # rear wheel frame
    F.orient_axis(E, E.y, q8)  # front wheel frame

    # Define points
    no = Point("no")  # Global origin
    no.set_vel(N, 0)
    dn = no.locatenew("dn", q1 * N.x + q2 * N.y)  # rear wheel contact point
    do = dn.locatenew("do", rr * cross(C.y, cross(C.y, A.z)).normalize())
    co = do.locatenew("co", l1 * C.x + l2 * C.z)  # rear frame center of mass
    ce = do.locatenew("ce", d1 * C.x)  # Steer axis
    fo = ce.locatenew("fo", d2 * E.z + d3 * E.x)  # Front frame center of mass
    eo = fo.locatenew("eo", l3 * E.x + l4 * E.z)  # Front wheel center of mass
    # Front wheel contact point
    fn = fo.locatenew("fn", -rf * cross(E.y, cross(E.y, A.z)).normalize())

    # Create bodies
    rear = RigidBody("rear", co, C, mc, (inertia(C, ic11, ic22, ic33, 0, 0, ic31), co))
    front = RigidBody("front", eo, E, me,
                      (inertia(E, ie11, ie22, ie33, 0, 0, ie31), eo))
    wheel_rear = RigidBody("wheel_rear", do, D, md,
                           (inertia(D, id11, id22, id11, 0, 0, 0), do))
    wheel_front = RigidBody("wheel_front", fo, F, mf,
                            (inertia(F, if11, if22, if11, 0, 0, 0), fo))
    bodies = [rear, front, wheel_rear, wheel_front]

    # Define constraints
    config_constrs = [dot(fn.pos_from(dn), A.z)]
    v_f = fo.vel(N) + cross(F.ang_vel_in(N), fn.pos_from(fo))
    v_r = dn.vel(N) + cross(D.ang_vel_in(B), dn.pos_from(do))
    vel_constrs = [
        config_constrs[0].diff(t),  # derivative of the holonomic constraint
        dot(v_r, N.x),
        dot(v_f, N.x),
        dot(v_r, N.y),
        dot(v_f, N.y),
    ]

    do.set_vel(N, cross(D.ang_vel_in(N), do.pos_from(dn)))
    fo.set_vel(N, cross(F.ang_vel_in(N), fo.pos_from(fn)))

    # Define kinematical differential equations
    kdes = [
        q1.diff(t) - u1, q2.diff(t) - u2, q3.diff(t) - u3, q4.diff(t) - u4,
        q5.diff(t) - u5, q6.diff(t) - u6, q7.diff(t) - u7, q8.diff(t) - u8
    ]

    # Define loads
    loads = [(body.masscenter, body.mass * g * A.z) for body in bodies]

    # Define KanesMethod
    q_ind = [q1, q2, q3, q4, q6, q7, q8]
    q_dep = [q5]
    u_ind = [u4, u6, u7]
    u_dep = [u1, u2, u3, u5, u8]

    return KanesMethod(N, q_ind=q_ind, u_ind=u_ind, kd_eqs=kdes,
                       q_dependent=q_dep, configuration_constraints=config_constrs,
                       u_dependent=u_dep, velocity_constraints=vel_constrs,
                       bodies=bodies, forcelist=loads, constraint_solver="CRAMER")


@benchmark(rounds=ROUNDS, group="Whipple bicycle Moore")
def test_whipple_bicycle_minimal_coordinates():
    return create_whipple_bicycle_moore_minimal_coords()


@benchmark(rounds=ROUNDS, group="Whipple bicycle Moore")
def test_whipple_bicycle_moore_full_coordinates():
    return create_whipple_bicycle_moore_full_coords()


@benchmark(rounds=ROUNDS, group="Whipple bicycle Moore", constraint_solver="CRAMER")
def test_whipple_bicycle_moore_brim():
    return create_whipple_bicycle_moore_brim()
