from __future__ import annotations

import pytest
from brim.bicycle.wheels import KnifeEdgeWheel, ToroidalWheel


class TestWheelsGeneral:
    @pytest.mark.parametrize("wheel", [KnifeEdgeWheel("wheel"), ToroidalWheel("wheel")])
    def test_default(self, wheel) -> None:
        wheel.define_connections()
        wheel.define_objects()
        wheel.define_kinematics()
        wheel.define_loads()
        assert wheel.name == "wheel"
        assert wheel.frame == wheel.body.frame
        assert wheel.center == wheel.body.masscenter
        assert wheel.rotation_axis == wheel.y


class TestKnifeEdgeWheel:
    def test_descriptions(self) -> None:
        wheel = KnifeEdgeWheel("wheel")
        wheel.define_objects()
        assert wheel.descriptions[wheel.radius] is not None


class TestToroidalWheel:
    def test_descriptions(self) -> None:
        wheel = ToroidalWheel("wheel")
        wheel.define_objects()
        assert wheel.descriptions[wheel.radius] is not None
        assert wheel.descriptions[wheel.transverse_radius] is not None
