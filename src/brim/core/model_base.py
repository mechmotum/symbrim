"""Module containing the base class for all models in BRiM."""
from __future__ import annotations

from abc import ABCMeta
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable

from sympy import symbols
from sympy.physics.mechanics._system import System

from brim.core.registry import Registry

try:  # pragma: no cover
    from bicycleparameters import Bicycle
except ImportError:  # pragma: no cover
    Bicycle = None

if TYPE_CHECKING:
    from sympy import Symbol

    from brim.core.requirement import ConnectionRequirement, ModelRequirement

__all__ = ["ConnectionBase", "ConnectionMeta", "LoadGroupBase", "LoadGroupMeta",
           "ModelBase", "ModelMeta", "set_default_formulation"]


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


class LoadGroupMeta(ABCMeta):
    """Metaclass for the :class:`brim.core.model_base.LoadGroupBase`."""

    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa: N804
        """Create a new class."""
        instance = super().__new__(mcs, name, bases, namespace, **kwargs)
        Registry().register_load_group(instance)
        return instance


class BrimBase:
    """Base class defining a common interface for the models and connections."""

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
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the object."""
        return {}

    def get_description(self, obj: Any) -> str:
        """Get description of a given object."""
        if obj in self.descriptions:
            return self.descriptions[obj]
        if hasattr(self, "submodels"):
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
        """System object used to store the information of the model itself.

        Notes
        -----
        This system object is used to store the information of the model itself. It does
        not by definition contain any information about the submodels or connections.
        Therefore, one cannot use this system object to form the equations of motion.
        Instead, one should use the :meth:`to_system` method to get the system object
        representing the entire model.
        """
        return self._system

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get a parameters mapping of a model based on a bicycle parameters object."""
        if Bicycle is None:
            raise ImportError("The bicycle parameters package is not installed.")
        return {}

    def define_objects(self) -> None:
        """Define the objects of the system."""

    def define_kinematics(self) -> None:
        """Define the kinematics of the system."""

    def define_loads(self) -> None:
        """Define the loads of the system."""

    def define_constraints(self) -> None:
        """Define the constraints of the system."""


class LoadGroupBase(BrimBase, metaclass=LoadGroupMeta):
    """Base class for the load groups."""

    parent: ModelBase | ConnectionBase | tuple[ModelBase | ConnectionBase, ...]

    def __init__(self, name: str) -> None:
        """Create a new instance of the load group.

        Parameters
        ----------
        name : str
            Name of the load group.
        """
        super().__init__(name)
        self._parent = None

    @property
    def parent(self) -> ModelBase | ConnectionBase | None:
        """Parent model or connection."""
        return self._parent

    @parent.setter
    def parent(self, parent: ModelBase | ConnectionBase) -> None:
        if self._parent is not None:
            raise ValueError(f"Load group is already used by {self.parent}")
        elif not isinstance(parent, self.__annotations__["parent"]):
            raise TypeError(
                f"Parent should be of type {self.__annotations__['parent']}")
        self._parent = parent


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
        self._load_groups = []
        for req in self.required_models:
            setattr(self, f"_{req.attribute_name}", None)

    @property
    def submodels(self) -> frozenset[ModelBase]:
        """Submodels of the connection."""
        submodels = []
        for req in self.required_models:
            submodels.append(getattr(self, req.attribute_name))
        return frozenset(submodel for submodel in submodels if submodel is not None)

    @property
    def load_groups(self) -> frozenset[LoadGroupBase]:
        """Load groups of the connection."""
        return frozenset(self._load_groups)

    def add_load_groups(self, *load_groups: LoadGroupBase) -> None:
        """Add load groups to the connection."""
        for load_group in load_groups:
            load_group.parent = self
        self._load_groups.extend(load_groups)

    def define_objects(self) -> None:
        """Define the objects in the connection."""
        for group in self._load_groups:
            group.define_objects()

    def define_kinematics(self) -> None:
        """Define the kinematics of the connection."""
        for group in self._load_groups:
            group.define_kinematics()

    def define_loads(self) -> None:
        """Define the loads on the connection."""
        for group in self._load_groups:
            group.define_loads()

    def define_constraints(self) -> None:
        """Define the constraints on the connection."""
        for group in self._load_groups:
            group.define_constraints()


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
        self._load_groups = []
        for req in self.required_models:
            setattr(self, f"_{req.attribute_name}", None)
        for req in self.required_connections:
            setattr(self, f"_{req.attribute_name}", None)

    @property
    def submodels(self) -> frozenset[ModelBase]:
        """Submodels out of which this model exists."""
        submodels = []
        for req in self.required_models:
            submodels.append(getattr(self, req.attribute_name))
        return frozenset(submodel for submodel in submodels if submodel is not None)

    @property
    def connections(self) -> frozenset[ConnectionBase]:
        """Submodels out of which this model exists."""
        connections = []
        for req in self.required_connections:
            connections.append(getattr(self, req.attribute_name))
        return frozenset(conn for conn in connections if conn is not None)

    @property
    def load_groups(self) -> frozenset[LoadGroupBase]:
        """Load groups of the connection."""
        return frozenset(self._load_groups)

    def add_load_groups(self, *load_groups: LoadGroupBase) -> None:
        """Add load groups to the connection."""
        for load_group in load_groups:
            load_group.parent = self
        self._load_groups.extend(load_groups)

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
        for group in self._load_groups:
            group.define_objects()

    def define_kinematics(self) -> None:
        """Establish the kinematics of the objects belonging to the model."""
        for submodel in self.submodels:
            submodel.define_kinematics()
        for group in self._load_groups:
            group.define_kinematics()

    def define_loads(self) -> None:
        """Define the loads that are acting upon the model."""
        for submodel in self.submodels:
            submodel.define_loads()
        for group in self._load_groups:
            group.define_loads()

    def define_constraints(self) -> None:
        """Define the constraints on the model."""
        for submodel in self.submodels:
            submodel.define_constraints()
        for group in self._load_groups:
            group.define_constraints()

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

    def to_system(self) -> System:
        """Export the model to a single system instance."""

        def get_systems(model):
            """Get the systems of the submodels."""
            return ([model.system] + [conn.system for conn in model.connections] +
                    [s for submodel in model.submodels for s in get_systems(submodel)])

        return _merge_systems(*get_systems(self))


def set_default_formulation(formulation: str
                            ) -> Callable[[type[ModelBase]], type[ModelBase]]:
    """Set the default formulation for a model."""

    def decorator(model: type[ModelBase]) -> type[ModelBase]:
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


def _merge_systems(*systems: System) -> System:  # pragma: no cover
    """Combine multiple system instance into one.

    Notes
    -----
    This function is not used in the current implementation of brim.
    However, it should in the end be moved to sympy mechanics.
    """
    system = System(systems[0].origin, systems[0].frame)
    for s in systems:
        if s is None:
            continue
        for qi in s.q_ind:
            if qi not in system.q:
                system.add_coordinates(qi, independent=True)
        for qi in s.q_dep:
            if qi not in system.q:
                system.add_coordinates(qi, independent=False)
        for ui in s.u_ind:
            if ui not in system.u:
                system.add_speeds(ui, independent=True)
        for ui in s.u_dep:
            if ui not in system.u:
                system.add_speeds(ui, independent=False)
        for body in s.bodies:
            if body not in system.bodies:
                system.add_bodies(body)
        for joint in s.joints:
            if joint not in system.joints:
                system.add_joints(joint)
        for load in s.loads:
            if load not in system.loads:
                system.add_loads(load)
        for kde in s.kdes:
            if kde not in system.kdes:
                system.add_kdes(kde)
        for fh in s.holonomic_constraints:
            if fh not in system.holonomic_constraints:
                system.add_holonomic_constraints(fh)
        for fnh in s.nonholonomic_constraints:
            if fnh not in system.nonholonomic_constraints:
                system.add_nonholonomic_constraints(fnh)
    return system
