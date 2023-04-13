from __future__ import annotations

import pytest
from brim.bicycle.grounds import FlatGround
from brim.bicycle.tyre_models import NonHolonomicTyreModel, _set_pos_contact_point
from brim.bicycle.wheels import KnifeEdgeWheel, ToroidalWheel
from brim.core import ModelBase, Requirement
from sympy import cos, sin
from sympy.physics.mechanics import Point, ReferenceFrame, dynamicsymbols
from sympy.physics.mechanics.system import System


class TestComputeContactPoint:
    @pytest.fixture()
    def _setup_flat_ground(self):
        self.ground = FlatGround("ground")
        self.ground.define_objects()
        self.ground.define_kinematics()
        self.contact_point = Point("contact_point")
        self.q = dynamicsymbols("q1:4")
        self.int_frame = ReferenceFrame("int_frame")
        self.int_frame.orient_body_fixed(self.ground.frame, (*self.q[:2], 0), "zxy")

    def test_knife_edge_wheel_on_flat_ground(self, _setup_flat_ground):
        wheel = KnifeEdgeWheel("wheel")
        wheel.define_objects()
        wheel.frame.orient_axis(self.int_frame, self.q[2], self.int_frame.y)
        _set_pos_contact_point(self.contact_point, self.ground, wheel)
        assert (self.contact_point.pos_from(wheel.center) -
                wheel.symbols["r"] * self.int_frame.z).express(wheel.frame).simplify(
        ).xreplace({self.q[1]: 0.123, self.q[2]: 1.234}) == 0
        # sqrt(cos(q2)**2) is not simplified

    def test_toroidal_wheel_on_flat_ground(self, _setup_flat_ground) -> None:
        wheel = ToroidalWheel("wheel")
        wheel.define_objects()
        wheel.frame.orient_axis(self.int_frame, self.q[2], self.int_frame.y)
        _set_pos_contact_point(self.contact_point, self.ground, wheel)
        assert (self.contact_point.pos_from(wheel.center) -
                wheel.symbols["r"] * self.int_frame.z + wheel.symbols["tr"] *
                self.ground.normal).express(wheel.frame).simplify().xreplace(
            {self.q[1]: 0.123, self.q[2]: 1.234}) == 0
        # sqrt(cos(q2)**2) is not simplified


class TestNonHolonomicTyreModel:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        class Model(ModelBase):
            required_models = (
                Requirement("ground", FlatGround, "Submodel of the ground."),
                Requirement("wheel", KnifeEdgeWheel, "Submodel of the wheel."),
            )
            required_connections = (
                Requirement("tyre_model", NonHolonomicTyreModel,
                            "Tyre model for the wheel."),
                )
            ground: FlatGround
            wheel: KnifeEdgeWheel
            tyre_model: NonHolonomicTyreModel

            def define_connections(self) -> None:
                super().define_connections()
                self.tyre_model.ground = self.ground
                self.tyre_model.wheel = self.wheel

            def define_objects(self) -> None:
                super().define_objects()
                self.tyre_model.define_objects()

            def define_kinematics(self) -> None:
                super().define_kinematics()
                self.tyre_model.define_kinematics()

            def define_loads(self) -> None:
                super().define_loads()
                self.tyre_model.define_loads()

        self.model = Model("model")
        self.model.ground = FlatGround("ground")
        self.model.wheel = KnifeEdgeWheel("wheel")
        self.model.tyre_model = NonHolonomicTyreModel("tyre_model")

    def test_default(self) -> None:
        self.model.define_connections()
        self.model.define_objects()
        assert self.model.tyre_model.name == "tyre_model"
        assert isinstance(self.model.tyre_model.system, System)

    @pytest.mark.parametrize("on_ground", [True, False])
    def test_compute_on_ground(self, on_ground: bool) -> None:
        self.model.define_connections()
        self.model.define_objects()
        self.model.tyre_model.on_ground = on_ground
        ground, wheel, tyre_model = (
            self.model.ground, self.model.wheel, self.model.tyre_model)
        t = dynamicsymbols._t
        q1, q2, x, y, z = dynamicsymbols("q1 q2 x y z")
        wheel.frame.orient_body_fixed(ground.frame, (q1, q2, 0), "zyx")
        tyre_model.contact_point.set_pos(
            ground.origin, (x * ground.planar_vectors[0] + y * ground.planar_vectors[1]
                            + int(not on_ground) * z * ground.normal))
        self.model.define_kinematics()
        self.model.define_loads()
        fnh = [
            wheel.radius * cos(q1) * q2.diff(t) + x.diff(t),
            wheel.radius * sin(q1) * q2.diff(t) + y.diff(t),
        ]
        assert len(tyre_model.system.holonomic_constraints) == int(not on_ground)
        assert len(tyre_model.system.nonholonomic_constraints) == 2
        if not on_ground:
            assert (tyre_model.system.holonomic_constraints[0] - z
                    ).simplify() == 0
        for fnhi in tyre_model.system.nonholonomic_constraints:
            assert (fnhi - fnh[0]).simplify() == 0 or (fnhi - fnh[1]).simplify() == 0
