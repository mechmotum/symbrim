from __future__ import annotations

import pytest
from brim.bicycle import PedalsBase, SimplePedals
from brim.utilities.testing import _test_descriptions
from sympy.physics.mechanics import Point, ReferenceFrame, Vector

try:
    from brim.utilities.plotting import PlotModel
    from symmeplot import PlotLine
except ImportError:
    PlotLine = None


@pytest.mark.parametrize("pedal_cls", [SimplePedals])
class TestPedalsBase:
    @pytest.fixture(autouse=True)
    def _setup(self, pedal_cls) -> None:
        self.pedals = pedal_cls("pedals")
        self.pedals.define_all()

    def test_types(self) -> None:
        assert isinstance(self.pedals, PedalsBase)
        assert isinstance(self.pedals.frame, ReferenceFrame)
        assert isinstance(self.pedals.center_point, Point)
        assert isinstance(self.pedals.left_pedal_point, Point)
        assert isinstance(self.pedals.right_pedal_point, Point)
        assert isinstance(self.pedals.rotation_axis, Vector)

    def test_descriptions(self) -> None:
        _test_descriptions(self.pedals)


class TestSimplePedals:
    def test_kinematics(self) -> None:
        pedals = SimplePedals("pedals")
        pedals.define_all()
        assert pedals.rotation_axis == pedals.frame.y
        assert pedals.right_pedal_point.pos_from(pedals.left_pedal_point).dot(
            pedals.rotation_axis) == 2 * pedals.symbols["offset"]
        assert pedals.right_pedal_point.pos_from(pedals.left_pedal_point).dot(
            pedals.frame.x) == 2 * pedals.symbols["radius"]

    @pytest.mark.skipif(PlotModel is None, reason="symmeplot not installed")
    def test_set_plot_objects(self):
        pedals = SimplePedals("pedals")
        pedals.define_all()
        plot_model = PlotModel(pedals.system.frame, pedals.system.origin, pedals)
        assert len(plot_model.children) == 1
        assert isinstance(plot_model.children[0], PlotLine)
