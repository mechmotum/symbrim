from __future__ import annotations

import pytest
from brim.bicycle.wheels import KnifeEdgeWheel, ToroidalWheel

try:
    from brim.utilities.plotting import PlotModel
    from symmeplot import PlotBody
    from symmeplot.plot_artists import Circle3D
except ImportError:
    PlotModel = None


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

    @pytest.mark.skipif(PlotModel is None, reason="symmeplot not installed")
    def test_plotting(self):
        wheel = KnifeEdgeWheel("wheel")
        wheel.define_all()

        plot_model = PlotModel(wheel.system.frame, wheel.system.fixed_point, wheel)
        assert len(plot_model.children) == 1
        assert isinstance(plot_model.children[0], PlotBody)
        assert any(isinstance(art, Circle3D) for art in plot_model.artists)


class TestToroidalWheel:
    def test_descriptions(self) -> None:
        wheel = ToroidalWheel("wheel")
        wheel.define_objects()
        assert wheel.descriptions[wheel.radius] is not None
        assert wheel.descriptions[wheel.transverse_radius] is not None
