from __future__ import annotations

import pytest
from brim.bicycle import CranksBase, MasslessCranks
from brim.utilities.testing import _test_descriptions
from sympy.physics.mechanics import Point, ReferenceFrame, Vector

try:
    from brim.utilities.plotting import PlotModel
    from symmeplot import PlotLine
except ImportError:
    PlotModel = None


@pytest.mark.parametrize("cranks_cls", [MasslessCranks])
class TestCranksBase:
    @pytest.fixture(autouse=True)
    def _setup(self, cranks_cls) -> None:
        self.cranks = cranks_cls("cranks")
        self.cranks.define_all()

    def test_types(self) -> None:
        assert isinstance(self.cranks, CranksBase)
        assert isinstance(self.cranks.frame, ReferenceFrame)
        assert isinstance(self.cranks.center_point, Point)
        assert isinstance(self.cranks.left_pedal_point, Point)
        assert isinstance(self.cranks.right_pedal_point, Point)
        assert isinstance(self.cranks.rotation_axis, Vector)

    def test_descriptions(self) -> None:
        _test_descriptions(self.cranks)


class TestMasslessCranks:
    def test_kinematics(self) -> None:
        cranks = MasslessCranks("cranks")
        cranks.define_all()
        assert cranks.rotation_axis == cranks.frame.y
        assert cranks.right_pedal_point.pos_from(cranks.left_pedal_point).dot(
            cranks.rotation_axis) == 2 * cranks.symbols["offset"]
        assert cranks.right_pedal_point.pos_from(cranks.left_pedal_point).dot(
            cranks.frame.x) == 2 * cranks.symbols["radius"]

    @pytest.mark.skipif(PlotModel is None, reason="symmeplot not installed")
    def test_plotting(self):
        cranks = MasslessCranks("cranks")
        cranks.define_all()
        plot_model = PlotModel(cranks.system.frame, cranks.system.origin, cranks)
        assert len(plot_model.children) == 1
        assert isinstance(plot_model.children[0], PlotLine)
