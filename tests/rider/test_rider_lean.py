import pytest
from brim.bicycle import RigidRearFrame
from brim.rider import RiderLean, RiderLeanMixin
from brim.utilities import to_system
from sympy import Matrix, Symbol, simplify, sin, zeros
from sympy.physics.mechanics import Point


class TestRiderLean:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.rear = RigidRearFrame("rear")
        self.rear.add_mixin(RiderLeanMixin)
        self.rear.rider = RiderLean("rider")

    def test_default(self) -> None:
        assert self.rear.rider.name == "rider"
        assert self.rear.rider.body.frame == self.rear.rider.frame
        assert self.rear.rider.lean_axis == self.rear.rider.x
        assert isinstance(self.rear.rider.lean_point, Point)
        assert isinstance(self.rear.lean_point, Point)

    @pytest.mark.parametrize("symbol_name", ["d_lp_x", "d_lp_z", "d1", "l1", "l2"])
    def test_mixin_descriptions(self, symbol_name) -> None:
        assert self.rear.get_description(self.rear.symbols[symbol_name]) is not None

    def test_dynamics(self):
        g = Symbol("g")
        q, d_lp = self.rear.q[0], self.rear.rider.symbols["d_lp"]
        m = self.rear.rider.body.mass
        ixx = self.rear.rider.body.central_inertia.to_matrix(self.rear.rider.frame)[0]
        self.rear.define_kinematics()
        self.rear.define_loads()
        system = to_system(self.rear)
        system.apply_gravity(g * self.rear.z)
        system.form_eoms()
        assert simplify(system.mass_matrix - Matrix([d_lp ** 2 * m + ixx])) == zeros(1)
        assert simplify(system.forcing - Matrix([g * d_lp * m * sin(q)])) == zeros(1)

    def test_set_rear_lean_axis(self):
        self.rear.lean_axis = self.rear.y
        assert self.rear.lean_axis == self.rear.y
        with pytest.raises(TypeError):
            self.rear.lean_axis = 1

    def test_set_rider_lean_axis(self):
        self.rear.rider.lean_axis = self.rear.y
        assert self.rear.rider.lean_axis == self.rear.y
        with pytest.raises(TypeError):
            self.rear.rider.lean_axis = 1

    def test_rider_descriptions(self):
        for length in self.rear.rider.symbols.values():
            assert self.rear.rider.descriptions[length] is not None
