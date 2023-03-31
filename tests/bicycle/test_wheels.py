from __future__ import annotations

import pytest
from brim.bicycle.grounds import FlatGround
from brim.bicycle.tyre_models import NonHolonomicTyreModel
from brim.bicycle.wheels import KnifeEdgeWheel
from sympy import Symbol
from sympy.physics.mechanics import ReferenceFrame, dynamicsymbols


class TestKnifeEdgeWheel:
    def test_default(self) -> None:
        wheel = KnifeEdgeWheel("wheel")
        assert wheel.name == "wheel"
        assert wheel.frame == wheel.body.frame
        assert wheel.center == wheel.body.masscenter
        assert wheel.rotation_axis == wheel.y
        assert wheel.tyre_model is None
        assert isinstance(wheel.radius, Symbol)

    def test_descriptions(self) -> None:
        wheel = KnifeEdgeWheel("wheel")
        assert wheel.descriptions[wheel.radius] is not None

    def test_tyre_model(self) -> None:
        wheel = KnifeEdgeWheel("wheel")
        wheel.tyre_model = NonHolonomicTyreModel("tyre_model")
        assert wheel.tyre_model is not None
        with pytest.raises(TypeError):
            wheel.tyre_model = KnifeEdgeWheel("not_a_tyre_model")

    def test_contact_point(self) -> None:
        q1, q2, q3 = dynamicsymbols("q1:4")
        wheel = KnifeEdgeWheel("wheel")
        ground = FlatGround("ground")
        int_frame = ReferenceFrame("int_frame")
        int_frame.orient_body_fixed(ground.frame, (q1, q2, 0), "zxy")
        wheel.frame.orient_axis(int_frame, q3, int_frame.y)
        wheel.compute_contact_point(ground)
        assert (wheel.contact_point.pos_from(wheel.center) -
                wheel.symbols["r"] * int_frame.z).express(wheel.frame).simplify(
        ).xreplace({q2: 0.123, q3: 1.234}) == 0  # sqrt(cos(q2)**2) is not simplified
