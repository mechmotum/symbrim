import pytest

from brim.bicycle import (
    KnifeEdgeWheel,
    NonHolonomicTire,
    TireBase,
    ToroidalWheel,
    WheelBase,
)
from brim.core import LoadGroupBase, Registry
from brim.core.requirement import ConnectionRequirement, ModelRequirement
from brim.other.rolling_disc import RollingDisc
from brim.rider import PinElbowSpringDamper, PinElbowStickLeftArm, PinElbowTorque


class TestRegistry:
    @pytest.mark.parametrize("model", [WheelBase, KnifeEdgeWheel, RollingDisc,
                                       ToroidalWheel])
    def test_models_registered(self, model) -> None:
        assert model in Registry().models

    @pytest.mark.parametrize("conn", [NonHolonomicTire])
    def test_connections_registered(self, conn) -> None:
        assert conn in Registry().connections

    @pytest.mark.parametrize("load_group", [PinElbowTorque, PinElbowSpringDamper])
    def test_load_groups_registered(self, load_group) -> None:
        assert load_group in Registry().load_groups

    def test_connections_and_models_split(self) -> None:
        assert Registry().models.isdisjoint(Registry().connections)

    @pytest.mark.parametrize(("args", "kwargs", "subset", "disjoint"), [
        ((ModelRequirement("wheel", WheelBase, "Wheel model."),), {},
         {KnifeEdgeWheel, ToroidalWheel},
         {NonHolonomicTire, RollingDisc, WheelBase}),
        ((ConnectionRequirement("tire", TireBase, "Tire model."),), {},
         {NonHolonomicTire},
         {KnifeEdgeWheel, ToroidalWheel, TireBase, RollingDisc, WheelBase}),
        ((ModelRequirement("wheel", WheelBase, "Wheel model."),),
         {"drop_abstract": False},
         {KnifeEdgeWheel, ToroidalWheel, WheelBase},
         {NonHolonomicTire, RollingDisc}),
        ((ConnectionRequirement("tire", TireBase, "Tire model."),),
         {"drop_abstract": False},
         {NonHolonomicTire, TireBase},
         {KnifeEdgeWheel, ToroidalWheel, RollingDisc, WheelBase}),
    ])
    def test_get_from_requirement(self, args, kwargs, subset, disjoint) -> None:
        options = set(Registry().get_from_requirement(*args, **kwargs))
        assert subset.issubset(options)
        assert disjoint.isdisjoint(options)

    def test_get_from_requirement_error(self) -> None:
        with pytest.raises(TypeError):
            Registry().get_from_requirement(WheelBase)

    @pytest.mark.parametrize(("args", "kwargs", "subset", "disjoint"), [
        ((RollingDisc("disc"), "wheel"), {},
         {KnifeEdgeWheel, ToroidalWheel}, {NonHolonomicTire, WheelBase, RollingDisc}),
        ((RollingDisc, "wheel"), {},
         {KnifeEdgeWheel, ToroidalWheel}, {NonHolonomicTire, WheelBase, RollingDisc}),
        ((RollingDisc("disc"), "tire"), {},
         {NonHolonomicTire}, {TireBase, KnifeEdgeWheel, RollingDisc}),
        ((RollingDisc("disc"), "wheel"), {"drop_abstract": False},
         {KnifeEdgeWheel, ToroidalWheel, WheelBase}, {NonHolonomicTire, RollingDisc}),
        ((RollingDisc("disc"), "tire"), {"drop_abstract": False},
         {NonHolonomicTire, TireBase}, {KnifeEdgeWheel, RollingDisc}),
    ])
    def test_get_from_property(self, args, kwargs, subset, disjoint) -> None:
        options = set(Registry().get_from_property(*args, **kwargs))
        assert subset.issubset(options)
        assert disjoint.isdisjoint(options)

    def test_get_from_property_error(self) -> None:
        with pytest.raises(ValueError):
            Registry().get_from_property(RollingDisc("disc"), "not_a_submodel")

    @pytest.mark.parametrize(("args", "kwargs", "subset", "disjoint"), [
        ((PinElbowStickLeftArm("arm"),), {},
         {PinElbowTorque, PinElbowSpringDamper}, {LoadGroupBase, PinElbowStickLeftArm}),
        ((PinElbowStickLeftArm,), {},
         {PinElbowTorque, PinElbowSpringDamper}, {LoadGroupBase, PinElbowStickLeftArm}),
        ((PinElbowStickLeftArm("arm"),), {"drop_abstract": False},
         {PinElbowTorque, PinElbowSpringDamper, LoadGroupBase}, {PinElbowStickLeftArm}),
    ])
    def test_get_applicable_load_groups(self, args, kwargs, subset, disjoint) -> None:
        options = set(Registry().get_matching_load_groups(*args, **kwargs))
        assert subset.issubset(options)
        assert disjoint.isdisjoint(options)
