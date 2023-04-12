from __future__ import annotations

import pytest
from brim.bicycle.grounds import FlatGround
from brim.bicycle.tyre_models import NonHolonomicTyreModel
from brim.bicycle.wheels import KnifeEdgeWheel
from sympy import cos, sin
from sympy.physics.mechanics import dynamicsymbols
from sympy.physics.mechanics.system import System


class TestNonHolonomicTyreModel:
    def test_default(self) -> None:
        tyre_model = NonHolonomicTyreModel("tyre_model")
        tyre_model.define_objects()
        assert tyre_model.name == "tyre_model"
        assert isinstance(tyre_model.system, System)

    @pytest.mark.parametrize("on_ground", [True, False])
    def test_compute_on_ground(self, on_ground: bool) -> None:
        t = dynamicsymbols._t
        q1, q2, x, y, z = dynamicsymbols("q1 q2 x y z")
        ground = FlatGround("ground")
        ground.define_objects()
        wheel = KnifeEdgeWheel("wheel")
        wheel.tyre_model = NonHolonomicTyreModel("tyre_model")
        wheel.define_objects()
        wheel.frame.orient_body_fixed(ground.frame, (q1, q2, 0), "zyx")
        wheel.contact_point.set_pos(
            ground.origin, (x * ground.planar_vectors[0] + y * ground.planar_vectors[1]
                            + int(not on_ground) * z * ground.normal))
        wheel.compute_contact_point(ground)
        wheel.compute_tyre_model(ground, on_ground)
        fnh = [
            wheel.radius * cos(q1) * q2.diff(t) + x.diff(t),
            wheel.radius * sin(q1) * q2.diff(t) + y.diff(t),
        ]
        assert len(wheel.tyre_model.system.holonomic_constraints) == int(not on_ground)
        assert len(wheel.tyre_model.system.nonholonomic_constraints) == 2
        if not on_ground:
            assert (wheel.tyre_model.system.holonomic_constraints[0] - z
                    ).simplify() == 0
        for fnhi in wheel.tyre_model.system.nonholonomic_constraints:
            assert (fnhi - fnh[0]).simplify() == 0 or (fnhi - fnh[1]).simplify() == 0
