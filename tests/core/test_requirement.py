from __future__ import annotations

import re

import pytest
from brim.core import ModelBase, Requirement


class MyModel(ModelBase):
    """My model description.

    Explanation
    -----------
    Explanation of this submodel.
    """


class MyOtherSubModel(ModelBase):
    """My other sub model description."""


class TestRequirement:
    def test_default(self) -> None:
        req = Requirement("my_sub_model_attr", MyModel)
        assert req.attribute_name == "my_sub_model_attr"
        assert req.types == (MyModel,)
        assert req.description == "My model description."
        assert req.full_name == "My sub model attr"
        assert req.type_name == "MyModel"
        assert str(req) == "my_sub_model_attr"
        assert re.match(r"Requirement\(.+\)$", repr(req))

    @pytest.mark.parametrize("args, kwargs, attribute, expected", [
        (("my_sub", MyModel), {"description": "New desc."}, "description", "New desc."),
        (("my_sub", MyModel), {"full_name": "New name"}, "full_name", "New name"),
        (("my_sub", MyModel), {"type_name": "New type"}, "type_name", "New type"),
    ])
    def test_specify_args(self, args, kwargs, attribute, expected) -> None:
        req = Requirement(*args, **kwargs)
        assert getattr(req, attribute) == expected

    def test_multiple_types(self) -> None:
        req = Requirement("my_sub", (MyModel, MyOtherSubModel))
        assert req.types == (MyModel, MyOtherSubModel)
        assert req.type_name == "MyModel or MyOtherSubModel"

    @pytest.mark.parametrize("attribute_name", ["my sub model", "my,sub_model"])
    def test_invalid_attribute_name(self, attribute_name) -> None:
        with pytest.raises(ValueError):
            Requirement(attribute_name, MyModel)
