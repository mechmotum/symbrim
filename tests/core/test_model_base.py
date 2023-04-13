from __future__ import annotations

import pytest
from brim.bicycle import FlatGround, KnifeEdgeWheel, NonHolonomicTyreModel
from brim.core import ModelBase
from brim.other.rolling_disc import RollingDisc
from sympy.physics.mechanics.system import System


class TestModelBase:
    """Test the ModelBase class.

    Explanation
    -----------
    As ModelBase is an abstract class, this test actually uses the rolling disc to test
    certain characteristics of the ModelBase class.
    """

    @pytest.fixture()
    def _create_model(self) -> None:
        self.disc = RollingDisc("rolling_disc")
        self.disc.disc = KnifeEdgeWheel("disc")
        self.disc.ground = FlatGround("ground")
        self.disc.tyre = NonHolonomicTyreModel("tyre")
        self.disc.define_connections()
        self.disc.define_objects()

    def test_init(self) -> None:
        disc = RollingDisc("model")
        assert isinstance(disc, ModelBase)
        assert str(disc) == "model"
        assert disc.name == "model"
        assert disc.disc is None
        assert disc.ground is None
        assert disc.tyre is None

    @pytest.mark.parametrize("name", ["", " ", "my model", "my,model", "my:model"])
    def test_invalid_name(self, name) -> None:
        with pytest.raises(ValueError):
            RollingDisc(name)

    def test_invalid_model(self) -> None:
        disc = RollingDisc("model")
        with pytest.raises(TypeError):
            disc.disc = FlatGround("ground")

    def test_invalid_connection(self) -> None:
        disc = RollingDisc("model")
        with pytest.raises(TypeError):
            disc.tyre = KnifeEdgeWheel("disc")

    def test_overwrite_submodel_of_connection(self, _create_model) -> None:
        self.disc.tyre.wheel = KnifeEdgeWheel("disc2")
        assert self.disc.tyre.wheel.name == "disc2"

    def test_invalid_submodel_of_connection(self, _create_model) -> None:
        with pytest.raises(TypeError):
            self.disc.tyre.ground = KnifeEdgeWheel("disc")

    def test_get_description_own_description(self, _create_model) -> None:
        assert (self.disc.disc.get_description(self.disc.disc.radius) ==
                self.disc.disc.descriptions[self.disc.disc.radius])

    def test_get_description_of_submodel(self, _create_model) -> None:
        assert self.disc.get_description(self.disc.disc.radius) is not None

    def test_get_description_of_not_existing_symbol(self, _create_model) -> None:
        assert self.disc.get_description("not existing symbol") is None

    def test_call_system(self, _create_model) -> None:
        self.disc.define_kinematics()
        self.disc.define_loads()
        assert isinstance(self.disc.system, System)
