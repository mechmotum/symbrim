from __future__ import annotations

import pytest
from brim.bicycle import FlatGround, KnifeEdgeWheel, NonHolonomicTyre
from brim.core import ModelBase, Registry, set_default_formulation
from brim.other.rolling_disc import RollingDisc
from sympy.physics.mechanics._system import System


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
        self.disc.define_constraints()
        assert isinstance(self.disc.system, System)


class TestFromFormulation:
    @pytest.fixture(autouse=True)
    def _setup_registry(self, request) -> None:
        def activate_registry():
            old_reg.activate()

        old_reg = Registry()
        old_reg.deactivate()
        request.addfinalizer(activate_registry)

        @set_default_formulation("default_formulation")
        class MyModel(ModelBase):
            pass

        class MyModel2(MyModel):
            formulation = "default_formulation"

        class MyModel3(MyModel):
            formulation = "other_formulation"

        class MyModel4(MyModel):
            formulation = "double_formulation"

        class MyModel5(MyModel):
            formulation = "double_formulation"

        self.MyModel, self.MyModel2, self.MyModel3, self.MyModel4, self.MyModel5 = (
            MyModel, MyModel2, MyModel3, MyModel4, MyModel5)

    def test_formulation_string(self) -> None:
        assert self.MyModel.formulation == ""
        assert self.MyModel2.formulation == "default_formulation"
        assert self.MyModel3.formulation == "other_formulation"

    def test_default_formulation(self) -> None:
        model = self.MyModel("model")
        assert model.formulation == "default_formulation"
        assert isinstance(model, self.MyModel2)

    def test_formulation_argument(self) -> None:
        model = self.MyModel.from_formulation("other_formulation", "model")
        assert model.formulation == "other_formulation"
        assert isinstance(model, self.MyModel3)

    def test_not_existing_formulation(self) -> None:
        with pytest.raises(ValueError):
            self.MyModel.from_formulation("not existing formulation", "model")

    def test_double_formulation(self) -> None:
        with pytest.raises(ValueError):
            self.MyModel.from_formulation("double_formulation", "model")

    def test_direct_instantiation(self) -> None:
        model = self.MyModel4("model")
        assert model.formulation == "double_formulation"
        assert isinstance(model, self.MyModel4)

    def test_set_default_formulation_invalid_type(self) -> None:
        with pytest.raises(TypeError):
            @set_default_formulation("my_formulation")
            class A:
                pass
