from __future__ import annotations

import re

import pytest
from brim.core import Connection, ModelBase, Requirement


class MyModel(ModelBase):
    """My model description.

    Explanation
    -----------
    Explanation of this submodel.
    """


class MyOtherSubModel(ModelBase):
    """My other sub model description."""


class TestRequirement:
    @pytest.mark.parametrize("req_class", [Requirement, Connection])
    def test_default(self, req_class) -> None:
        req = req_class("my_sub_model_attr", MyModel)
        assert req.attribute_name == "my_sub_model_attr"
        assert req.types == (MyModel,)
        assert req.description == "My model description."
        assert req.full_name == "My sub model attr"
        assert req.type_name == "MyModel"
        assert str(req) == "my_sub_model_attr"
        assert re.match(rf"^{req_class.__name__}\(.+\)$", repr(req))

    def test_is_submodel(self):
        assert Requirement("my_sub", MyModel).is_submodel
        assert not Connection("my_sub", MyModel).is_submodel

    @pytest.mark.parametrize("req_class", [Requirement, Connection])
    @pytest.mark.parametrize("args, kwargs, attribute, expected", [
        (("my_sub", MyModel), {"description": "New desc."}, "description", "New desc."),
        (("my_sub", MyModel), {"full_name": "New name"}, "full_name", "New name"),
        (("my_sub", MyModel), {"type_name": "New type"}, "type_name", "New type"),
    ])
    def test_specify_args(self, req_class, args, kwargs, attribute, expected) -> None:
        req = req_class(*args, **kwargs)
        assert getattr(req, attribute) == expected

    @pytest.mark.parametrize("req_class", [Requirement, Connection])
    def test_multiple_types(self, req_class) -> None:
        req = req_class("my_sub", (MyModel, MyOtherSubModel))
        assert req.types == (MyModel, MyOtherSubModel)
        assert req.type_name == "MyModel or MyOtherSubModel"

    @pytest.mark.parametrize("req_class", [Requirement, Connection])
    @pytest.mark.parametrize("attribute_name", ["my sub model", "my,sub_model"])
    def test_invalid_attribute_name(self, req_class, attribute_name) -> None:
        with pytest.raises(ValueError):
            req_class(attribute_name, MyModel)
