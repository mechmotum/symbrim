from __future__ import annotations

from typing import Any

import pytest
from brim.bicycle import FlatGround, KnifeEdgeWheel, NonHolonomicTyre
from brim.core import LoadGroupBase, ModelBase, Registry, set_default_convention
from brim.other.rolling_disc import RollingDisc
from sympy import Symbol
from sympy.physics.mechanics import Torque
from sympy.physics.mechanics._system import System


class MyLoad(LoadGroupBase):
    required_parent_type = KnifeEdgeWheel

    @property
    def descriptions(self) -> dict[Any, str]:
        """Dictionary of descriptions of the load group's attributes."""
        return {
            **super().descriptions,
            self.symbols["T"]: "Torque applied to the disc.",
        }

    def _define_objects(self) -> None:
        """Define the objects in the load group."""
        self.symbols["T"] = Symbol(self._add_prefix("T"))

    def _define_loads(self) -> None:
        """Define the loads in the load group."""
        self.system.add_loads(Torque(
            self.parent.frame, self.symbols["T"] * self.parent.rotation_axis))


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
        self.disc.tyre = NonHolonomicTyre("tyre")
        self.load_group = MyLoad("load")
        self.disc.disc.add_load_groups(self.load_group)

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
        self.disc.define_connections()
        self.disc.define_objects()
        self.disc.tyre.wheel = KnifeEdgeWheel("disc2")
        assert self.disc.tyre.wheel.name == "disc2"

    def test_invalid_submodel_of_connection(self, _create_model) -> None:
        with pytest.raises(TypeError):
            self.disc.tyre.ground = KnifeEdgeWheel("disc")

    def test_get_description_own_description(self, _create_model) -> None:
        self.disc.define_all()
        assert (self.disc.disc.get_description(self.disc.disc.radius) ==
                self.disc.disc.descriptions[self.disc.disc.radius])

    def test_get_description_of_submodel(self, _create_model) -> None:
        self.disc.define_all()
        assert self.disc.get_description(self.disc.disc.radius) is not None

    def test_get_description_of_load_group(self, _create_model) -> None:
        self.disc.define_all()
        assert self.disc.get_description(self.load_group.symbols["T"]) is not None

    def test_get_description_of_not_existing_symbol(self, _create_model) -> None:
        self.disc.define_all()
        assert self.disc.get_description(Symbol("not_existing_symbol")) is None

    def test_call_system(self, _create_model) -> None:
        self.disc.define_all()
        assert isinstance(self.disc.system, System)

    def test_load_group_default(self, _create_model) -> None:
        class MyEmptyLoad(LoadGroupBase):
            def __init__(self, name):
                super().__init__(name)
                self.called_objects = False
                self.called_kinematics = False
                self.called_loads = False
                self.called_constraints = False

            def _define_objects(self) -> None:
                self.called_objects = True

            def _define_kinematics(self) -> None:
                self.called_kinematics = True

            def _define_loads(self) -> None:
                self.called_loads = True

            def _define_constraints(self) -> None:
                self.called_constraints = True

        load_model = MyEmptyLoad("load1")
        load_conn = MyEmptyLoad("load2")
        self.disc.add_load_groups(load_model)
        self.disc.tyre.add_load_groups(load_conn)
        self.disc.define_all()
        assert load_model.called_objects
        assert load_model.called_kinematics
        assert load_model.called_loads
        assert load_model.called_constraints
        assert load_conn.called_objects
        assert load_conn.called_kinematics
        assert load_conn.called_loads
        assert load_conn.called_constraints

    def test_load_group_undefined_parent(self) -> None:
        load = MyLoad("load")
        assert load.parent is None
        assert load.system is None

    def test_load_group_invalid_parent(self) -> None:
        with pytest.raises(TypeError):
            FlatGround("ground").add_load_groups(MyLoad("load"))

    def test_load_grip_used_parent(self) -> None:
        wheel1 = KnifeEdgeWheel("wheel1")
        wheel2 = KnifeEdgeWheel("wheel2")
        load_group = MyLoad("load")
        wheel1.add_load_groups(load_group)
        with pytest.raises(ValueError):
            wheel2.add_load_groups(load_group)

    def test_to_system(self, _create_model) -> None:
        self.disc.define_all()
        system = self.disc.to_system()
        assert system.loads == (
            Torque(self.disc.disc.frame,
                   self.load_group.symbols["T"] * self.disc.disc.rotation_axis),)


class TestFromConvention:
    @pytest.fixture(autouse=True)
    def _setup_registry(self, request) -> None:
        def activate_registry():
            old_reg.activate()

        old_reg = Registry()
        old_reg.deactivate()
        request.addfinalizer(activate_registry)

        @set_default_convention("default_convention")
        class MyModel(ModelBase):
            pass

        class MyModel2(MyModel):
            convention = "default_convention"

        class MyModel3(MyModel):
            convention = "other_convention"

        class MyModel4(MyModel):
            convention = "double_convention"

        class MyModel5(MyModel):
            convention = "double_convention"

        self.MyModel, self.MyModel2, self.MyModel3, self.MyModel4, self.MyModel5 = (
            MyModel, MyModel2, MyModel3, MyModel4, MyModel5)

    def test_convention_string(self) -> None:
        assert self.MyModel.convention == ""
        assert self.MyModel2.convention == "default_convention"
        assert self.MyModel3.convention == "other_convention"

    def test_default_convention(self) -> None:
        model = self.MyModel("model")
        assert model.convention == "default_convention"
        assert isinstance(model, self.MyModel2)

    def test_convention_argument(self) -> None:
        model = self.MyModel.from_convention("other_convention", "model")
        assert model.convention == "other_convention"
        assert isinstance(model, self.MyModel3)

    def test_not_existing_convention(self) -> None:
        with pytest.raises(ValueError):
            self.MyModel.from_convention("not existing convention", "model")

    def test_double_convention(self) -> None:
        with pytest.raises(ValueError):
            self.MyModel.from_convention("double_convention", "model")

    def test_direct_instantiation(self) -> None:
        model = self.MyModel4("model")
        assert model.convention == "double_convention"
        assert isinstance(model, self.MyModel4)

    def test_set_default_convention_invalid_type(self) -> None:
        with pytest.raises(TypeError):
            @set_default_convention("my_convention")
            class A:
                pass
