from __future__ import annotations

from brim.core.mixins import NewtonianBodyMixin
from brim.core.model_base import ModelBase
from sympy.physics.mechanics import RigidBody


class MyModel(NewtonianBodyMixin, ModelBase):
    pass


class TestNewtonianBodyMixin:
    def test_mixin(self) -> None:
        model = MyModel("name")
        model.define_objects()
        assert isinstance(model.body, RigidBody)
        assert model.system.bodies[0] is model.body
        assert model.frame is model.body.frame
        assert model.x is model.frame.x
        assert model.y is model.frame.y
        assert model.z is model.frame.z
        assert model.system.origin is model.body.masscenter
