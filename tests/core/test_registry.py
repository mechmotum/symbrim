import pytest
from brim.bicycle import KnifeEdgeWheel, NonHolonomicTyre, ToroidalWheel, WheelBase
from brim.core import Registry
from brim.other.rolling_disc import RollingDisc


class TestRegistry:
    @pytest.mark.parametrize("model", [WheelBase, KnifeEdgeWheel, RollingDisc,
                                       ToroidalWheel])
    def test_models_registered(self, model) -> None:
        assert model in Registry().models

    @pytest.mark.parametrize("conn", [NonHolonomicTyre])
    def test_connections_registered(self, conn) -> None:
        assert conn in Registry().connections

    def test_connections_and_models_split(self) -> None:
        assert Registry().models.isdisjoint(Registry().connections)
