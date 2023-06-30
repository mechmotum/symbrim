from __future__ import annotations

import pytest
from brim.rider.pelvis import PelvisBase, PlanarPelvis
from brim.utilities.testing import _test_descriptions
from sympy.physics.mechanics import Point, RigidBody


@pytest.mark.parametrize("pelvis_cls", [PlanarPelvis])
class TestPelvisBase:
    def test_types(self, pelvis_cls) -> None:
        pelvis = pelvis_cls("pelvis")
        pelvis.define_objects()
        assert isinstance(pelvis, PelvisBase)
        assert isinstance(pelvis.body, RigidBody)
        assert isinstance(pelvis.left_hip_point, Point)
        assert isinstance(pelvis.right_hip_point, Point)

    def test_descriptions(self, pelvis_cls) -> None:
        _test_descriptions(pelvis_cls("pelvis"))


class TestSimpleRigidPelvis:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.pelvis = PlanarPelvis("pelvis")
        self.pelvis.define_objects()
        self.pelvis.define_kinematics()
        self.pelvis.define_loads()
        self.pelvis.define_constraints()

    def test_kinematics(self):
        assert self.pelvis.right_hip_point.pos_from(self.pelvis.left_hip_point).dot(
            self.pelvis.y) == self.pelvis.symbols["hip_width"]
