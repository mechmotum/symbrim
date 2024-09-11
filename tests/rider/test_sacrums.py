from __future__ import annotations

import pytest
from sympy import eye

from brim.rider.base_connections import SacrumBase
from brim.rider.pelvis import PlanarPelvis
from brim.rider.sacrums import FixedSacrum
from brim.rider.torso import PlanarTorso
from brim.utilities.testing import _test_descriptions, create_model_of_connection

try:
    from brim.utilities.plotting import PlotConnection
except ImportError:
    PlotConnection = None


@pytest.mark.parametrize("pelvis_cls, torso_cls, sacrum_cls", [
    (PlanarPelvis, PlanarTorso, FixedSacrum),
])
class TestSacrumBase:
    @pytest.fixture(autouse=True)
    def _setup(self, pelvis_cls, torso_cls, sacrum_cls) -> None:
        self.model = create_model_of_connection(sacrum_cls)("model")
        self.model.pelvis = pelvis_cls("pelvis")
        self.model.torso = torso_cls("torso")
        self.model.conn = sacrum_cls("sacrum")
        self.pelvis, self.torso, self.conn = (
            self.model.pelvis, self.model.torso, self.model.conn)
        self.model.define_all()

    def test_types(self) -> None:
        assert isinstance(self.conn, SacrumBase)

    def test_descriptions(self) -> None:
        _test_descriptions(self.conn)

    @pytest.mark.skipif(PlotConnection is None, reason="symmeplot not installed")
    def test_plotting(self):
        plot_conn = PlotConnection(self.conn.system.frame,
                                   self.conn.system.fixed_point, self.conn)
        assert plot_conn.children


class TestFixedSacrum:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = create_model_of_connection(FixedSacrum)("model")
        self.model.pelvis = PlanarPelvis("pelvis")
        self.model.torso = PlanarTorso("torso")
        self.model.conn = FixedSacrum("sacrum")
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
