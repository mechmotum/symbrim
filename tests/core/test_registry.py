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

    @pytest.mark.parametrize("requirement, subset, disjoint", [
        (ModelRequirement("wheel", WheelBase, "Wheel model."),
         {KnifeEdgeWheel, ToroidalWheel},
         {NonHolonomicTyre, RollingDisc, WheelBase}),
        (ConnectionRequirement("tyre", TyreBase, "Tyre model."),
         {NonHolonomicTyre},
         {KnifeEdgeWheel, ToroidalWheel, TyreBase, RollingDisc, WheelBase}),
    ])
    def test_get_from_requirement_default(self, requirement, subset, disjoint) -> None:
        assert subset.issubset(Registry().get_from_requirement(requirement))
        assert disjoint.isdisjoint(Registry().get_from_requirement(requirement))

    @pytest.mark.parametrize("args, kwargs, subset, disjoint", [
        ((ModelRequirement("wheel", WheelBase, "Wheel model."),),
         {"drop_abstract": False},
         {KnifeEdgeWheel, ToroidalWheel, WheelBase},
         {NonHolonomicTyre, RollingDisc}),
        ((ConnectionRequirement("tyre", TyreBase, "Tyre model."),),
         {"drop_abstract": False},
         {NonHolonomicTyre, TyreBase},
         {KnifeEdgeWheel, ToroidalWheel, RollingDisc, WheelBase}),
    ])
    def test_get_from_requirement_custom(self, args, kwargs, subset, disjoint) -> None:
        assert subset.issubset(Registry().get_from_requirement(*args, **kwargs))
        assert disjoint.isdisjoint(Registry().get_from_requirement(*args, **kwargs))
