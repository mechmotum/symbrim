"""Module containing the base class for all models in BRiM."""
from __future__ import annotations

from abc import ABCMeta
from functools import wraps
from typing import TYPE_CHECKING, Any

from sympy import symbols

from brim.core.registry import Registry

try:  # pragma: no cover
    from bicycleparameters import Bicycle
except ImportError:  # pragma: no cover
    Bicycle = None

if TYPE_CHECKING:
    from sympy import Symbol
    from sympy.physics.mechanics._system import System

    from brim.core.requirement import ConnectionRequirement, ModelRequirement

__all__ = ["ConnectionBase", "ConnectionMeta", "ModelBase", "ModelMeta",
           "set_default_formulation"]


def _get_requirements(bases, namespace, req_attr_name):
    requirements = {}
    for base_cls in bases:
        base_reqs = getattr(base_cls, req_attr_name, None)
        if base_reqs is not None:
            for req in base_reqs:
                requirements[req.attribute_name] = req
    if req_attr_name in namespace:
        for req in namespace[req_attr_name]:
            requirements[req.attribute_name] = req
    return tuple(requirements.values())


def _create_submodel_property(requirement: ModelRequirement) -> property:
    def getter(self):
        return getattr(self, f"_{requirement.attribute_name}")

    def setter(self, model):
        if not (model is None or isinstance(model, requirement.types)):
            raise TypeError(
                f"{requirement.full_name} should be an instance of an subclass of "
                f"{requirement.type_name}, but {model!r} is an instance of "
                f"{type(model)}.")
        setattr(self, f"_{requirement.attribute_name}", model)

    getter.__annotations__ = {"return": requirement.type_hint}
    setter.__annotations__ = {"model": requirement.type_hint, "return": None}
    return property(getter, setter, None, requirement.description)


def _create_connection_property(requirement: ConnectionRequirement) -> property:
    def getter(self):
        return getattr(self, f"_{requirement.attribute_name}")

    def setter(self, conn):
        if not (conn is None or isinstance(conn, requirement.types)):
            raise TypeError(
                f"{requirement.full_name} should be an instance of an subclass "
                f"of {requirement.type_name}, but {conn!r} is an instance of "
                f"{type(conn)}.")
        setattr(self, f"_{requirement.attribute_name}", conn)
        conn._parent = self

    getter.__annotations__ = {"return": requirement.type_hint}
    setter.__annotations__ = {"conn": requirement.type_hint, "return": None}
    return property(getter, setter, None, requirement.description)


class ModelMeta(ABCMeta):
    """Metaclass for the :class:`brim.core.model_base.ModelBase`."""

    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa: N804
        """Create a new class."""
        # Create properties for each of the requirements
        requirements = _get_requirements(bases, namespace, "required_models")
        for req in requirements:
            namespace[req.attribute_name] = _create_submodel_property(req)
        namespace["required_models"] = tuple(requirements)  # Update the requirements
        # Create properties for each of the requirements
        requirements = _get_requirements(bases, namespace, "required_connections")
        for req in requirements:
            namespace[req.attribute_name] = _create_connection_property(req)
        namespace["required_connections"] = tuple(requirements)  # Update
        instance = super().__new__(mcs, name, bases, namespace, **kwargs)
        Registry().register_model(instance)
        return instance


class ConnectionMeta(ABCMeta):
    """Metaclass for the :class:`brim.core.model_base.ConnectionBase`."""

    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa: N804
        """Create a new class."""
        # Create properties for each of the requirements
        requirements = _get_requirements(bases, namespace, "required_models")
        for req in requirements:
            namespace[req.attribute_name] = _create_submodel_property(req)
        namespace["required_models"] = tuple(requirements)  # Update the requirements
        instance = super().__new__(mcs, name, bases, namespace, **kwargs)
        Registry().register_connection(instance)
        return instance


class BrimBase:
    """Base class defining a common interfact for the models and connections."""

    def __init__(self, name: str) -> None:
        """Create a new instance.

        Parameters
        ----------
        name : str
            Name of the object.
        """
        if not name.isidentifier():
            raise ValueError("The name of an object should be a valid identifier.")
        self._name = str(name)
        self._system = None
        self.symbols: dict[str, Any] = {}

    def _add_prefix(self, names: str) -> str:
        """Add the name of the object as a prefix to a set of names.

        Explanation
        -----------
        Helper function to add the name of the object as a prefix to a set of names.
        This is used to create unique names for the objects in the model.
        """
        syms = symbols(names)
        if isinstance(syms, tuple):
            return ", ".join(f"{self.name}_{sym.name}" for sym in syms)
        return f"{self.name}_{syms.name}"

    @property
    def name(self) -> str:
        """Name of the object."""
        return self._name

    def __str__(self) -> str:
        return self.name

    @property
    def submodels(self) -> frozenset[ModelBase]:
        """Submodels out of which this model exists."""
        submodels = []
        for req in self.required_models:
            submodels.append(getattr(self, req.attribute_name))
        return frozenset(submodel for submodel in submodels if submodel is not None)

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the object."""
        return {}

    def get_description(self, obj: Any) -> str:
        """Get description of a given object."""
        if obj in self.descriptions:
            return self.descriptions[obj]
        if hasattr(self, "submodels"):  # pragma: no cover  (is always True)
            for submodel in self.submodels:
                desc = submodel.get_description(obj)
                if desc is not None:
                    return desc
        if hasattr(self, "connections"):
            for conn in self.connections:
                desc = conn.get_description(obj)
                if desc is not None:
                    return desc

    @property
    def system(self) -> System | None:
        """System object representing the model."""
        return self._system

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get a parameters mapping of a model based on a bicycle parameters object."""
        if Bicycle is None:
            raise ImportError("The bicycle parameters package is not installed.")
        return {}


class ConnectionBase(BrimBase, metaclass=ConnectionMeta):
    """Base class for all connections in brim."""

    required_models: tuple[ModelRequirement, ...] = ()

    def __init__(self, name: str) -> None:
        """Create a new instance of the connection.

        Parameters
        ----------
        name : str
            Name of the connection.
        """
        super().__init__(name)
        self._parent = None
        for req in self.required_models:
            setattr(self, f"_{req.attribute_name}", None)

    def define_objects(self) -> None:
        """Define the objects in the connection."""

    def define_kinematics(self) -> None:
        """Define the kinematics of the connection."""

    def define_loads(self) -> None:
        """Define the loads on the connection."""

    def define_constraints(self) -> None:
        """Define the constraints on the connection."""


class ModelBase(BrimBase, metaclass=ModelMeta):
    """Base class for all objects in brim."""

    required_models: tuple[ModelRequirement, ...] = ()
    required_connections: tuple[ConnectionRequirement, ...] = ()
    formulation: str = ""

    def __init__(self, name: str) -> None:
        """Create a new instance of the model.

        Parameters
        ----------
        name : str
            Name of the model.
        """
        super().__init__(name)
        for req in self.required_models:
            setattr(self, f"_{req.attribute_name}", None)
        for req in self.required_connections:
            setattr(self, f"_{req.attribute_name}", None)

    @property
    def connections(self) -> frozenset[ConnectionBase]:
        """Submodels out of which this model exists."""
        connections = []
        for req in self.required_connections:
            connections.append(getattr(self, req.attribute_name))
        return frozenset(conn for conn in connections if conn is not None)

    @classmethod
    def from_formulation(cls, formulation: str, name: str, *args, **kwargs
                         ) -> ModelBase:
        """Create a model from a formulation."""
        possible_models = []
        for model in Registry().models:
            if issubclass(model, cls) and model.formulation == formulation:
                possible_models.append(model)
        if len(possible_models) == 0:
            raise ValueError(f"No model found for formulation {formulation!r} of type "
                             f"{cls}.")
        if len(possible_models) > 1:
            raise ValueError(f"Multiple models found for formulation {formulation!r} "
                             f"of type {cls}: {set(possible_models)}.")
        return possible_models[0](name, *args, **kwargs)

    def define_connections(self) -> None:
        """Define the submodels used by connections in the model."""
        for submodel in self.submodels:
            submodel.define_connections()

    def define_objects(self) -> None:
        """Initialize the objects belonging to the model."""
        for submodel in self.submodels:
            submodel.define_objects()

    def define_kinematics(self) -> None:
        """Establish the kinematics of the objects belonging to the model."""
        for submodel in self.submodels:
            submodel.define_kinematics()

    def define_loads(self) -> None:
        """Define the loads that are acting upon the model."""
        for submodel in self.submodels:
            submodel.define_loads()

    def define_constraints(self) -> None:
        """Define the constraints on the model."""
        for submodel in self.submodels:
            submodel.define_constraints()

    def define_all(self) -> None:
        """Define all aspects of the model."""
        self.define_connections()
        self.define_objects()
        self.define_kinematics()
        self.define_loads()
        self.define_constraints()

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get a parameters mapping of a model based on a bicycle parameters object."""
        params = super().get_param_values(bicycle_parameters)
        for submodel in self.submodels:
            params.update(submodel.get_param_values(bicycle_parameters))
        for conn in self.connections:
            params.update(conn.get_param_values(bicycle_parameters))
        return params


def set_default_formulation(formulation: str) -> None:
    """Set the default formulation for a model."""

    def decorator(model: ModelBase) -> ModelBase:
        old_new = model.__new__

        @wraps(old_new)
        def new_new(cls, *args, **kwargs) -> ModelBase:
            if cls is model:
                return cls.from_formulation(formulation, *args, **kwargs)
            return old_new(cls)

        if not issubclass(model, ModelBase):
            raise TypeError(f"Model {model} is not a subclass of ModelBase.")
        model.__new__ = new_new
        return model

    return decorator
