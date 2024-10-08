from __future__ import annotations

import pytest
from sympy.physics.mechanics import Point, RigidBody

from symbrim.rider.torso import PlanarTorso, TorsoBase
from symbrim.utilities.testing import _test_descriptions

try:
    from symbrim.utilities.plotting import PlotModel
except ImportError:
    PlotModel = None


@pytest.mark.parametrize("torso_cls", [PlanarTorso])
class TestTorsoBase:
    def test_types(self, torso_cls) -> None:
        torso = torso_cls("torso")
        torso.define_objects()
        assert isinstance(torso, TorsoBase)
        assert isinstance(torso.body, RigidBody)
        assert isinstance(torso.left_shoulder_point, Point)
        assert isinstance(torso.right_shoulder_point, Point)

    def test_descriptions(self, torso_cls) -> None:
        _test_descriptions(torso_cls("torso"))

    @pytest.mark.skipif(PlotModel is None, reason="symmeplot not installed")
    def test_plotting(self, torso_cls):
        torso = torso_cls("torso")
        torso.define_all()
        plot_model = PlotModel(torso.system.frame, torso.system.fixed_point, torso)
        assert plot_model.children


class TestSimpleRigidTorso:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.torso = PlanarTorso("torso")
        self.torso.define_objects()
        self.torso.define_kinematics()
        self.torso.define_loads()
        self.torso.define_constraints()

    def test_kinematics(self):
        w = self.torso.symbols["shoulder_width"]
        h = self.torso.symbols["shoulder_height"]
        assert self.torso.right_shoulder_point.pos_from(
            self.torso.left_shoulder_point).dot(self.torso.y) == w
        assert self.torso.right_shoulder_point.pos_from(
            self.torso.body.masscenter).dot(self.torso.z) == -h
