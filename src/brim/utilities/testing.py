"""Module containing utilities for testing."""
from __future__ import annotations

from sympy.physics.mechanics import System

from brim.core import ConnectionBase, ConnectionRequirement, LoadGroupBase, ModelBase


def _test_descriptions(instance: ModelBase | ConnectionBase | LoadGroupBase) -> None:
    """Test if all symbols have descriptions."""
    if isinstance(instance, ConnectionBase):
        for model in instance.submodels:
            model.define_connections()
            model.define_objects()
        instance.define_objects()
    elif isinstance(instance, LoadGroupBase):
        instance.define_objects()
    else:
        instance.define_connections()
        instance.define_objects()
    for sym in instance.symbols.values():
        assert sym in instance.descriptions
    for qi in instance.q:
        assert qi in instance.descriptions
    for ui in instance.u:
        assert ui in instance.descriptions


def create_model_of_connection(connection_cls: type[ConnectionBase]) -> type[ModelBase]:
    """Create a model which uses the connection."""
    required_connections = (ConnectionRequirement("conn", connection_cls),)
    required_models = connection_cls.required_models

    def _define_connections(self):
        ModelBase._define_connections(self)
        for req in self.conn.required_models:
            model = getattr(self, req.attribute_name)
            if model is not None:
                setattr(self.conn, req.attribute_name, model)

    def _define_objects(self):
        ModelBase._define_objects(self)
        for conn in self.connections:
            conn.define_objects()
        self._system = System(self.conn.system.frame, self.conn.system.origin)

    def _define_kinematics(self):
        ModelBase._define_kinematics(self)
        for conn in self.connections:
            conn.define_kinematics()

    def _define_loads(self):
        ModelBase._define_loads(self)
        for conn in self.connections:
            conn.define_loads()

    def _define_constraints(self):
        ModelBase._define_constraints(self)
        for conn in self.connections:
            conn.define_constraints()

    return type("MyModel", (ModelBase,), {
        "required_connections": required_connections,
        "required_models": required_models,
        "define_connections": _define_connections,
        "_define_objects": _define_objects,
        "_define_kinematics": _define_kinematics,
        "_define_loads": _define_loads,
        "_define_constraints": _define_constraints,
    })
