from __future__ import annotations

import pytest
from brim.bicycle.grounds import FlatGround
from sympy.physics.mechanics._system import System


class TestFlatGround:
    def test_default(self) -> None:
        ground = FlatGround("ground")
        ground.define_objects()
        assert ground.name == "ground"
        assert ground.frame == ground.body.frame
        assert ground.get_normal(ground.origin) == -ground.frame.z
        assert ground.get_tangent_vectors(ground.origin) == (
            ground.frame.x, ground.frame.y)
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
        ground.define_objects()
        vectors = (ground.frame.x, ground.frame.y, ground.frame.z)
        times = -1 if normal[0] == "-" else 1
        assert ground.get_normal(ground.origin) == times * vectors[n_idx]
        assert ground.get_tangent_vectors(ground.origin) == (
            vectors[pl_idx1], vectors[pl_idx2])
