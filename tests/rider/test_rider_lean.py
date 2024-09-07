import pytest
from sympy import Matrix, Symbol, simplify, sin, zeros
from sympy.physics.mechanics import Point

from brim.bicycle import RigidRearFrame
from brim.rider import RiderLean, RiderLeanConnection
from brim.utilities.testing import _test_descriptions, create_model_of_connection


class TestRiderLean:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.model = create_model_of_connection(RiderLeanConnection)("model")
        self.model.rear_frame = RigidRearFrame("rear_frame")
        self.model.rider = RiderLean("rider")
        self.model.conn = RiderLeanConnection("rear_rider")
        self.model.define_connections()
        self.model.define_objects()
        self.rear, self.rider, self.conn = (
            self.model.rear_frame, self.model.rider, self.model.conn)

    def test_default(self) -> None:
        assert self.rider.name == "rider"
        assert self.rider.body.frame == self.rider.frame
        assert self.rider.lean_axis == self.rider.x
        assert isinstance(self.rider.lean_point, Point)
        assert self.conn.lean_axis == self.rear.saddle.frame.x
        assert isinstance(self.conn.lean_point, Point)

    def test_connection_descriptions(self) -> None:
        _test_descriptions(self.conn)

    def test_model_descriptions(self) -> None:
        _test_descriptions(self.rider)

    def test_dynamics(self):
        g = Symbol("g")
        q, d_lp = self.conn.q[0], self.rider.symbols["d_lp"]
        m = self.rider.body.mass
        ixx = self.rider.body.central_inertia.to_matrix(self.rider.frame)[0]
        self.model.define_kinematics()
        self.model.define_loads()
        self.model.define_constraints()
        system = self.model.to_system()
        system.apply_uniform_gravity(g * self.rear.saddle.frame.z)
        system.form_eoms()
        assert simplify(system.mass_matrix - Matrix([d_lp ** 2 * m + ixx])) == zeros(1)
        assert simplify(system.forcing - Matrix([g * d_lp * m * sin(q)])) == zeros(1)

    def test_set_rear_lean_axis(self):
        self.conn.lean_axis = self.rear.saddle.frame.y
        assert self.conn.lean_axis == self.rear.saddle.frame.y
        with pytest.raises(ValueError):
            self.conn.lean_axis = 1
        with pytest.raises(ValueError):
            self.conn.lean_axis = self.rider.x

    def test_set_rider_lean_axis(self):
        self.rider.lean_axis = self.rider.y
        assert self.rider.lean_axis == self.rider.y
        with pytest.raises(ValueError):
            self.rider.lean_axis = 1
        with pytest.raises(ValueError):
            self.rider.lean_axis = self.rear.saddle.frame.x
