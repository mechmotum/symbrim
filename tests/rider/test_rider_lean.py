import pytest
from brim.bicycle import RigidRearFrame
from brim.core import ConnectionRequirement, ModelBase, ModelRequirement
from brim.rider import RiderLean, RiderLeanConnection
from brim.utilities import to_system
from sympy import Matrix, Symbol, simplify, sin, zeros
from sympy.physics.mechanics import Point
from sympy.physics.mechanics._system import System


class TestRiderLean:
    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        class Model(ModelBase):
            required_models: tuple[ModelRequirement, ...] = (
                ModelRequirement("rear_frame", RigidRearFrame, "Rear frame model."),
                ModelRequirement("rider", RiderLean, "Rider lean model."),
            )
            required_connections: tuple[ConnectionRequirement, ...] = (
                ConnectionRequirement("rider_connection", RiderLeanConnection,
                            "Rear to rider connection."),
            )
            rear_frame: RigidRearFrame
            rider: RiderLean
            rider_connection: RiderLeanConnection

            def define_connections(self) -> None:
                super().define_connections()
                self.rider_connection.rider = self.rider
                self.rider_connection.rear_frame = self.rear_frame

            def define_objects(self) -> None:
                super().define_objects()
                self._system = System.from_newtonian(self.rear_frame.body)
                self.rider_connection.define_objects()

            def define_kinematics(self) -> None:
                super().define_kinematics()
                self.rider_connection.define_kinematics()

            def define_loads(self) -> None:
                super().define_loads()
                self.rider_connection.define_loads()

            def define_constraints(self) -> None:
                super().define_constraints()
                self.rider_connection.define_constraints()

        self.model = Model("model")
        self.model.rear_frame = RigidRearFrame("rear_frame")
        self.model.rider = RiderLean("rider")
        self.model.rider_connection = RiderLeanConnection("rear_rider")
        self.model.define_connections()
        self.model.define_objects()
        self.rear, self.rider, self.conn = (
            self.model.rear_frame, self.model.rider, self.model.rider_connection)

    def test_default(self) -> None:
        assert self.rider.name == "rider"
        assert self.rider.body.frame == self.rider.frame
        assert self.rider.lean_axis == self.rider.x
        assert isinstance(self.rider.lean_point, Point)
        assert self.conn.lean_axis == self.rear.x
        assert isinstance(self.conn.lean_point, Point)

    @pytest.mark.parametrize("symbol_name", ["d_lp_x", "d_lp_z"])
    def test_rider_lean_connection_descriptions(self, symbol_name) -> None:
        assert self.model.get_description(self.conn.symbols[symbol_name]) is not None

    def test_dynamics(self):
        g = Symbol("g")
        q, d_lp = self.conn.q[0], self.rider.symbols["d_lp"]
        m = self.rider.body.mass
        ixx = self.rider.body.central_inertia.to_matrix(self.rider.frame)[0]
        self.model.define_kinematics()
        self.model.define_loads()
        self.model.define_constraints()
        system = to_system(self.model)
        system.apply_gravity(g * self.rear.z)
        system.form_eoms()
        assert simplify(system.mass_matrix - Matrix([d_lp ** 2 * m + ixx])) == zeros(1)
        assert simplify(system.forcing - Matrix([g * d_lp * m * sin(q)])) == zeros(1)

    def test_set_rear_lean_axis(self):
        self.conn.lean_axis = self.rear.y
        assert self.conn.lean_axis == self.rear.y
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
            self.rider.lean_axis = self.rear.x

    def test_rider_descriptions(self):
        for length in self.rider.symbols.values():
            assert self.rider.descriptions[length] is not None
