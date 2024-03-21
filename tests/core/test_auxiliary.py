import pytest
from brim.core.auxiliary import AuxiliaryData, AuxiliaryDataHandler
from sympy import simplify, solve, sqrt, symbols
from sympy.physics.mechanics import (
    Force,
    Particle,
    Point,
    ReferenceFrame,
    System,
    dynamicsymbols,
)


class AuxiliarySetup:
    @pytest.fixture(autouse=True)
    def _setup_cart_pendulum(self) -> None:
        """Cart with a two link pendulum."""
        self.x, self.v = dynamicsymbols("x v")
        self.q, self.u = dynamicsymbols("q:2"), dynamicsymbols("u:2")
        self.l = symbols("l:3")
        self.uay, self.fay, self.ual, self.fal = dynamicsymbols("uay fay ual fal")
        self.inertial_frame = ReferenceFrame("inertial_frame")
        self.inertial_point = Point("inertial_point")
        self.inertial_point.set_vel(self.inertial_frame, 0)
        self.f1 = ReferenceFrame("link1")
        self.f2 = ReferenceFrame("link2")
        self.f1.orient_axis(self.inertial_frame, self.q[0], self.inertial_frame.z)
        self.f1.set_ang_vel(self.inertial_frame, self.u[0] * self.inertial_frame.z)
        self.f2.orient_axis(self.f1, self.q[1], self.f1.z)
        self.f2.set_ang_vel(self.f1, self.u[1] * self.f1.z)
        self.cart = self.inertial_point.locatenew(
            "cart", self.x * self.inertial_frame.x)
        self.cart.set_vel(self.inertial_frame, self.v * self.inertial_frame.x)
        self.p1 = self.cart.locatenew("p1", -self.l[0] * self.f1.y)
        self.p2 = self.p1.locatenew("p2", -self.l[1] * self.f2.y)
        # Additional point attached to the first link.
        self.p3 = self.p1.locatenew("p3", self.l[2] * self.f1.x)
        self.p1.v2pt_theory(self.cart, self.inertial_frame, self.f1)
        self.p2.v2pt_theory(self.p1, self.inertial_frame, self.f2)
        # Don't define the velocity of p3 to possibly cause errors.

        self.ld_fz = AuxiliaryData(
            self.cart, self.inertial_frame.y, self.uay, self.fay)
        self.ld_j2 = AuxiliaryData(self.p1, -self.f2.y, self.ual, self.fal)
        self.noncontributing_loads = [self.ld_fz, self.ld_j2]

class TestAuxiliaryData(AuxiliarySetup):
    def test_init_force(self) -> None:
        assert self.ld_fz.location == self.cart
        assert self.ld_fz.direction == self.inertial_frame.y
        assert self.ld_fz.speed_symbol == self.uay
        assert self.ld_fz.load_symbol == self.fay

    def test_init_torque(self) -> None:
        with pytest.raises(NotImplementedError):
            AuxiliaryData(self.f1, self.inertial_frame.x, self.uay, self.fay)

    def test_is_force_torque(self) -> None:
        assert self.ld_fz.is_force
        assert not self.ld_fz.is_torque

    def test_get_load_force(self) -> None:
        force = self.ld_fz.get_load(self.inertial_frame)
        pytest.raises(ValueError, lambda: force.point.pos_from(self.inertial_point))
        assert isinstance(force, Force)
        assert force.point.vel(self.inertial_frame) == self.uay * self.inertial_frame.y
        assert force.point.acc(self.inertial_frame) == (
            self.uay.diff() * self.inertial_frame.y)
        assert force.force == self.fay * self.inertial_frame.y

    def test_auxiliary_velocity(self) -> None:
        assert self.ld_fz.auxiliary_velocity == self.uay * self.inertial_frame.y
        assert self.ld_j2.auxiliary_velocity == -self.ual * self.f2.y


class TestAuxiliaryHandler(AuxiliarySetup):
    @pytest.fixture(autouse=True)
    def _setup_graph(self) -> None:
        self.handler = AuxiliaryDataHandler(self.inertial_frame, self.inertial_point)
        self.handler.auxiliary_data_list.extend(self.noncontributing_loads)

    def test_init(self) -> None:
        assert self.handler.inertial_frame == self.inertial_frame
        assert self.handler.inertial_point == self.inertial_point
        assert self.handler.auxiliary_data_list == self.noncontributing_loads
        assert self.handler.auxiliary_forces_data == tuple(self.noncontributing_loads)
        assert self.handler.auxiliary_torques_data == ()

    def test_from_system(self) -> None:
        sys = System()
        handler = AuxiliaryDataHandler.from_system(sys)
        assert handler.inertial_frame == sys.frame
        assert handler.inertial_point == sys.fixed_point

    @pytest.mark.parametrize("get_childs", [
        "_pos_dict", lambda pt: pt._pos_dict.keys()])
    def test_create_tree(self, get_childs) -> None:
        tree = AuxiliaryDataHandler._extract_tree(self.inertial_point, get_childs)
        expected_tree = {
            self.inertial_point: [self.cart],
            self.cart: [self.p1],
            self.p1: [self.p2, self.p3],
            self.p2: [],
            self.p3: [],
        }
        assert set(tree) == set(expected_tree)
        for p, chlds in tree.items():
            assert set(chlds) == set(expected_tree[p])
            assert len(chlds) == len(expected_tree[p])

    def test_apply_speeds(self) -> None:
        self.handler.apply_speeds()
        cart_vel = self.v * self.inertial_frame.x + self.uay * self.inertial_frame.y
        p1_vel = cart_vel + self.l[0] * self.u[0] * self.f1.x - self.ual * self.f2.y
        p2_vel = p1_vel + self.l[1] * (self.u[0] + self.u[1]) * self.f2.x
        p3_vel = p1_vel + self.l[2] * self.u[0]  * self.f1.y
        assert self.cart.vel(self.inertial_frame) == cart_vel
        assert self.p1.vel(self.inertial_frame) == p1_vel
        assert self.p2.vel(self.inertial_frame) == p2_vel
        assert self.p3.vel(self.inertial_frame) == p3_vel

    def test_apply_speeds_double(self) -> None:
        self.handler.apply_speeds()
        pytest.raises(ValueError, lambda: self.handler.apply_speeds())

    def test_create_loads(self) -> None:
        loads = self.handler.create_loads()
        for ld in loads:
            with pytest.raises(ValueError):
                ld.point.pos_from(self.inertial_point)
        assert loads[0].point.vel(self.inertial_frame) == (
            self.uay * self.inertial_frame.y)
        assert loads[0].force == self.fay * self.inertial_frame.y
        assert loads[1].point.vel(self.inertial_frame) == -self.ual * self.f2.y
        assert loads[1].force == -self.fal * self.f2.y

    def test_sliding_box(self):
        sign = lambda x: x / sqrt(x**2)  # noqa: E731
        # Define the symbols.
        m, g, mu = symbols("m g mu")
        t = dynamicsymbols._t
        x, v, uaux, fext, fn = dynamicsymbols("x v uaux fext fn")

        # Initialize the system object.
        sb_sys = System()

        # Create the box.
        box = Particle("box", Point("box_o"), m)
        box.masscenter.set_pos(sb_sys.fixed_point, x * sb_sys.x)
        box.masscenter.set_vel(sb_sys.frame, (v) * sb_sys.x)
        sb_sys.add_bodies(box)

        # Specify the coordinates and speeds.
        sb_sys.q_ind = [x]
        sb_sys.u_ind = [v]
        sb_sys.kdes = [x.diff(t) - v]
        sb_sys.u_aux = [uaux]

        # Apply loads.
        sb_sys.apply_uniform_gravity(-g * sb_sys.y)
        sb_sys.add_loads(
            Force(box.masscenter, fext * sb_sys.x),  # Extenal force
            Force(box.masscenter, -sign(v) * mu * fn * sb_sys.x),  # Friction force
        )

        # Introduce noncontributing load.
        handler = AuxiliaryDataHandler(sb_sys.frame, sb_sys.fixed_point)
        handler.add_noncontributing_force(box.masscenter, sb_sys.y, uaux, fn)
        handler.apply_speeds()

        sb_sys.add_loads(*handler.create_loads())

        # Form the equations of motion.
        sb_sys.validate_system()
        eoms = sb_sys.form_eoms()

        # Test the output.
        aux_eqs = sb_sys.eom_method.auxiliary_eqs
        fn_eq = solve(aux_eqs, fn)[fn]
        assert fn_eq == g * m
        assert simplify((solve(eoms, v.diff(t))[v.diff(t)] -
                        (-mu * fn * sign(v) + fext)/m).xreplace({fn: fn_eq})) == 0
