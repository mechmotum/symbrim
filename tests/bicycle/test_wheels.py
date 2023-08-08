from __future__ import annotations

import pytest
from brim.bicycle.wheels import KnifeEdgeWheel, ToroidalWheel

try:
    from symmeplot import PlotBody
    from symmeplot.plot_artists import Circle3D
except ImportError:
    PlotBody = None


class TestWheelsGeneral:
    @pytest.mark.parametrize("wheel", [KnifeEdgeWheel("wheel"), ToroidalWheel("wheel")])
    def test_default(self, wheel) -> None:
        wheel.define_connections()
        wheel.define_objects()
        wheel.define_kinematics()
        wheel.define_loads()
        wheel.define_constraints()
        assert wheel.name == "wheel"
        assert wheel.frame == wheel.body.frame
        assert wheel.center == wheel.body.masscenter
        assert wheel.rotation_axis == wheel.y


class TestKnifeEdgeWheel:
    def test_descriptions(self) -> None:
        wheel = KnifeEdgeWheel("wheel")
        wheel.define_objects()
        assert wheel.descriptions[wheel.radius] is not None

    @pytest.mark.skipif(PlotBody is None, reason="symmeplot not installed")
    def test_get_plot_objects(self):
        wheel = KnifeEdgeWheel("wheel")
        wheel.define_all()
        objects = wheel.get_plot_objects(wheel.frame, wheel.system.origin)
        assert len(objects) == 1
        assert isinstance(objects[0], PlotBody)
        assert any(isinstance(art, Circle3D) for art in objects[0].artists)


class TestToroidalWheel:
    def test_descriptions(self) -> None:
        wheel = ToroidalWheel("wheel")
        wheel.define_objects()
        assert wheel.descriptions[wheel.radius] is not None
        assert wheel.descriptions[wheel.transverse_radius] is not None
