from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from brim.bicycle.grounds import FlatGround
from sympy.physics.mechanics.system import System

if TYPE_CHECKING:
    pass


class TestFlatGround:
    def test_default(self) -> None:
        ground = FlatGround("ground")
        assert ground.name == "ground"
        assert ground.frame == ground.body.frame
        assert ground.normal == -ground.frame.z
        assert ground.planar_vectors == (ground.frame.x, ground.frame.y)
        assert ground.origin == ground.body.masscenter
        assert ground.origin.vel(ground.frame) == 0
        assert isinstance(ground.system, System)

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
        vectors = (ground.frame.x, ground.frame.y, ground.frame.z)
        times = -1 if normal[0] == "-" else 1
        assert ground.normal == times * vectors[n_idx]
        assert ground.planar_vectors == (vectors[pl_idx1], vectors[pl_idx2])
