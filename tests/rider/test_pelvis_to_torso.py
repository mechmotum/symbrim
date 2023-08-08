from __future__ import annotations

import pytest
from brim.rider.base_connections import PelvisToTorsoBase
from brim.rider.pelvis import PlanarPelvis
from brim.rider.pelvis_to_torso import FixedPelvisToTorso
from brim.rider.torso import PlanarTorso
from brim.utilities.testing import _test_descriptions, create_model_of_connection
from sympy import eye

try:
    from brim.utilities.plotting import PlotConnection
except ImportError:
    PlotConnection = None


@pytest.mark.parametrize("pelvis_cls, torso_cls, pelvis_to_torso_cls", [
    (PlanarPelvis, PlanarTorso, FixedPelvisToTorso),
])
class TestPelvisToTorsoBase:
    @pytest.fixture(autouse=True)
    def _setup(self, pelvis_cls, torso_cls, pelvis_to_torso_cls) -> None:
        self.model = create_model_of_connection(pelvis_to_torso_cls)("model")
        self.model.pelvis = pelvis_cls("pelvis")
        self.model.torso = torso_cls("torso")
        self.model.conn = pelvis_to_torso_cls("pelvis_to_torso")
        self.pelvis, self.torso, self.conn = (
            self.model.pelvis, self.model.torso, self.model.conn)
        self.model.define_all()

    def test_types(self) -> None:
        assert isinstance(self.conn, PelvisToTorsoBase)

    def test_descriptions(self) -> None:
        _test_descriptions(self.conn)

    @pytest.mark.skipif(PlotConnection is None, reason="symmeplot not installed")
    def test_plotting(self):
        plot_conn = PlotConnection(self.conn.system.frame,
                                   self.conn.system.origin, self.conn)
        assert plot_conn.children


class TestFixedPelvisToTorso:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = create_model_of_connection(FixedPelvisToTorso)("model")
        self.model.pelvis = PlanarPelvis("pelvis")
        self.model.torso = PlanarTorso("torso")
        self.model.conn = FixedPelvisToTorso("pelvis_to_torso")
        self.pelvis, self.torso, self.conn = (
            self.model.pelvis, self.model.torso, self.model.conn)
        self.model.define_connections()
        self.model.define_objects()

    def test_default(self) -> None:
        self.model.define_kinematics()
        assert self.pelvis.body.masscenter.pos_from(self.torso.body.masscenter).express(
            self.pelvis.frame) == self.conn.symbols["d_p_t"] * self.pelvis.z
        assert self.pelvis.frame.dcm(self.torso.frame) == eye(3)

    def test_set_torso_wrt_pelvis(self) -> None:
        with pytest.raises(ValueError):
            self.conn.torso_wrt_pelvis = self.torso.z
        self.conn.torso_wrt_pelvis = 2 * self.pelvis.z
        self.model.define_kinematics()
        assert self.pelvis.body.masscenter.pos_from(self.torso.body.masscenter).express(
            self.pelvis.frame) == -2 * self.pelvis.z
