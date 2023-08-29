from __future__ import annotations

import pytest
from brim.bicycle.grounds import FlatGround
from sympy import Symbol
from sympy.physics.mechanics import Vector
from sympy.physics.mechanics._system import System

try:
    from brim.utilities.plotting import PlotModel
    from symmeplot import PlotFrame
except ImportError:
    PlotModel = None


class TestFlatGround:
    @pytest.fixture()
    def _setup(self) -> None:
        self.ground = FlatGround("ground")
        self.ground.define_objects()

    def test_default(self, _setup) -> None:
        assert self.ground.name == "ground"
        assert self.ground.frame == self.ground.body.frame
        assert self.ground.get_normal(self.ground.origin) == -self.ground.frame.z
        assert self.ground.get_tangent_vectors(self.ground.origin) == (
            self.ground.frame.x, self.ground.frame.y)
        assert self.ground.origin == self.ground.body.masscenter
        assert self.ground.origin.vel(self.ground.frame) == 0
        assert isinstance(self.ground.system, System)

    @pytest.mark.parametrize("normal, n_idx, pl_idx1, pl_idx2", [
        ("+x", 0, 1, 2),
        ("-x", 0, 1, 2),
        ("+y", 1, 0, 2),
        ("-y", 1, 0, 2),
        ("+z", 2, 0, 1),
        ("-z", 2, 0, 1),
        ("x", 0, 1, 2),
        ("y", 1, 0, 2),
        ("z", 2, 0, 1),
    ])
    def test_normal(self, normal: str, n_idx: int, pl_idx1: int, pl_idx2: int) -> None:
        ground = FlatGround("ground", normal)
        ground.define_objects()
        vectors = (ground.frame.x, ground.frame.y, ground.frame.z)
        times = -1 if normal[0] == "-" else 1
        assert ground.get_normal(ground.origin) == times * vectors[n_idx]
        assert ground.get_tangent_vectors(ground.origin) == (
            vectors[pl_idx1], vectors[pl_idx2])

    @pytest.mark.parametrize("tp", ["tuple", "vector", "point"])
    @pytest.mark.parametrize("position, expected", [
        ((Symbol("x"), Symbol("y"), Symbol("z")),
         (Symbol("x"), Symbol("y"), Symbol("z"))),
        ((Symbol("x"), Symbol("y")), (Symbol("x"), Symbol("y"), 0))])
    def test_parse_plane_position(self, _setup, tp, position, expected) -> None:
        if tp == "vector" or tp == "point":
            position = Vector(0)
            for i, v in enumerate("xyz"):
                if i < len(expected):
                    position += expected[i] * self.ground.frame[v]
        if tp == "point":
            position = self.ground.origin.locatenew("p", position)
        assert self.ground._parse_plane_position(position) == expected

    @pytest.mark.parametrize("position", [
        (Symbol("x"), Symbol("y"), Symbol("z"), Symbol("w")),
        (Symbol("x"), )])
    def test_parse_plane_position_error(self, _setup, position) -> None:
        with pytest.raises(ValueError):
            self.ground._parse_plane_position(position)

    @pytest.mark.skipif(PlotModel is None, reason="symmeplot not installed")
    def test_plotting(self):
        ground = FlatGround("ground")
        ground.define_all()
        plot_model = PlotModel(ground.system.frame, ground.system.origin, ground)
        assert len(plot_model.children) == 1
        assert isinstance(plot_model.children[0], PlotFrame)
