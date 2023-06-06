import pytest
from brim.bicycle import (
    KnifeEdgeWheel,
    NonHolonomicTyre,
    ToroidalWheel,
    TyreBase,
    WheelBase,
)
from brim.core import Registry
from brim.core.requirement import ConnectionRequirement, ModelRequirement
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

    @pytest.mark.parametrize("args, kwargs, subset, disjoint", [
        ((ModelRequirement("wheel", WheelBase, "Wheel model."),), {},
         {KnifeEdgeWheel, ToroidalWheel},
         {NonHolonomicTyre, RollingDisc, WheelBase}),
        ((ConnectionRequirement("tyre", TyreBase, "Tyre model."),), {},
         {NonHolonomicTyre},
         {KnifeEdgeWheel, ToroidalWheel, TyreBase, RollingDisc, WheelBase}),
        ((ModelRequirement("wheel", WheelBase, "Wheel model."),),
         {"drop_abstract": False},
         {KnifeEdgeWheel, ToroidalWheel, WheelBase},
         {NonHolonomicTyre, RollingDisc}),
        ((ConnectionRequirement("tyre", TyreBase, "Tyre model."),),
         {"drop_abstract": False},
         {NonHolonomicTyre, TyreBase},
         {KnifeEdgeWheel, ToroidalWheel, RollingDisc, WheelBase}),
    ])
    def test_get_from_requirement(self, args, kwargs, subset, disjoint) -> None:
        options = set(Registry().get_from_requirement(*args, **kwargs))
        assert subset.issubset(options)
        assert disjoint.isdisjoint(options)

    def test_get_from_requirement_error(self) -> None:
        with pytest.raises(TypeError):
            Registry().get_from_requirement(WheelBase)

    @pytest.mark.parametrize("args, kwargs, subset, disjoint", [
        ((RollingDisc("disc"), "disc"), {},
         {KnifeEdgeWheel, ToroidalWheel}, {NonHolonomicTyre, WheelBase, RollingDisc}),
        ((RollingDisc("disc"), "tyre"), {},
         {NonHolonomicTyre}, {TyreBase, KnifeEdgeWheel, RollingDisc}),
        ((RollingDisc("disc"), "disc"), {"drop_abstract": False},
         {KnifeEdgeWheel, ToroidalWheel, WheelBase}, {NonHolonomicTyre, RollingDisc}),
        ((RollingDisc("disc"), "tyre"), {"drop_abstract": False},
         {NonHolonomicTyre, TyreBase}, {KnifeEdgeWheel, RollingDisc}),
    ])
    def test_get_from_property(self, args, kwargs, subset, disjoint) -> None:
        options = set(Registry().get_from_property(*args, **kwargs))
        assert subset.issubset(options)
        assert disjoint.isdisjoint(options)

    def test_get_from_property_error(self) -> None:
        with pytest.raises(ValueError):
            Registry().get_from_property(RollingDisc("disc"), "wheel")
