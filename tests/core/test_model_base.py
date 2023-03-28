from __future__ import annotations

import pytest
from brim.utilities.templates import MyModel, MySubModel
from sympy.physics.mechanics.system import System


class TestModelBase:
    """Test the ModelBase class.

    Explanation
    -----------
    As ModelBase is an abstract class, this test actually uses the WhippleBicycleMoore
    to test certain characteristics of the ModelBase class.
    """

    @pytest.fixture()
    def _create_model(self) -> None:
        self.model = MyModel("model")
        self.model.submodel1 = MySubModel("submodel1")
        self.model.submodel2 = MySubModel("submodel2")

    def test_init(self) -> None:
        bike = MyModel("model")
        assert bike.name == "model"
        assert bike.submodel1 is None
        assert bike.submodel2 is None

    @pytest.mark.parametrize("name", ["", " ", "my model", "my,model", "my:model"])
    def test_invalid_name(self, name) -> None:
        with pytest.raises(ValueError):
            MyModel(name)

    @pytest.mark.parametrize("meth", ["define_kinematics", "define_loads"])
    def test_call_traversal(self, _create_model, meth) -> None:
        # Test should ideally also test for the correct order
        def register_call(meth):
            def wrapper():
                call_order.append(meth.__self__.name)
                return meth()

            return wrapper

        call_order = []
        for m in [self.model, self.model.submodel1, self.model.submodel2]:
            setattr(m, meth, register_call(getattr(m, meth)))
        getattr(self.model, meth)()
        assert set(call_order) == {"model", "submodel1", "submodel2"}

    def test_get_description_own_description(self, _create_model) -> None:
        assert (self.model.get_description(self.model.q[0]) ==
                self.model.descriptions[self.model.q[0]])

    def test_get_description_of_submodel(self, _create_model) -> None:
        assert self.model.get_description(self.model.submodel1.my_symbol) is not None

    def test_get_description_of_not_existing_symbol(self, _create_model) -> None:
        assert self.model.get_description("not existing symbol") is None

    def test_call_system(self, _create_model):
        self.model.define_kinematics()
        self.model.define_loads()
        assert isinstance(self.model.system, System)
