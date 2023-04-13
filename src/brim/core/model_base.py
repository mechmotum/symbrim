"""Module containing the base class for all models in BRiM."""
from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any

from sympy import symbols

if TYPE_CHECKING:
    from sympy.physics.mechanics import System

    from brim.core.requirement import ConnectionRequirement, ModelRequirement

__all__ = ["ConnectionBase", "ConnectionMeta", "ModelBase", "ModelMeta"]


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


class ModelMeta(ABCMeta):
    """Metaclass for the :class:`brim.core.model_base.ModelBase`."""

    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa: N804
        """Create a new class."""

        def create_submodel_property(requirement: ModelRequirement) -> property:
            def getter(self):
                return getattr(self, f"_{requirement.attribute_name}")

            def setter(self, model):
                if not (model is None or isinstance(model, requirement.types)):
                    raise TypeError(
                        f"{requirement.full_name} should be an instance of an subclass "
                        f"of {requirement.type_name}, but {model!r} is an instance of "
                        f"{type(model)}.")
                setattr(self, f"_{requirement.attribute_name}", model)

            getter.__annotations__ = {"return": requirement.type_hint}
            setter.__annotations__ = {"model": requirement.type_hint, "return": None}
            return property(getter, setter, None, requirement.description)

        def create_connection_property(requirement: ConnectionRequirement) -> property:
            def getter(self):
                return getattr(self, f"_{requirement.attribute_name}")

            def setter(self, conn):
                if not (conn is None or isinstance(conn, ConnectionBase)):
                    raise TypeError(
                        f"{requirement.full_name} should be an instance of an subclass "
                        f"of {ConnectionBase}, but {conn!r} is an instance of "
                        f"{type(conn)}.")
                setattr(self, f"_{requirement.attribute_name}", conn)
                for c_ref, m_ref in requirement.model_references.items():
                    # Set the protected attribute on the connection to retrieve the
                    # reference from the model it belongs to. The double lambda is
                    # required to bind the loop variable.
                    setattr(conn, f"_get_{c_ref}", (
                        lambda m_ref:
                        lambda self_conn: getattr(self, m_ref))(m_ref))  # noqa: B023

            getter.__annotations__ = {"return": ConnectionBase}
            setter.__annotations__ = {"conn": ConnectionBase, "return": None}
            return property(getter, setter, None, requirement.description)

        # Create properties for each of the requirements
        requirements = _get_requirements(bases, namespace, "required_models")
        for req in requirements:
            namespace[req.attribute_name] = create_submodel_property(req)
        namespace["required_models"] = tuple(requirements)  # Update the requirements
        # Create properties for each of the requirements
        requirements = _get_requirements(bases, namespace, "required_connections")
        for req in requirements:
            namespace[req.attribute_name] = create_connection_property(req)
        namespace["required_connections"] = tuple(requirements)  # Update
        return super().__new__(mcs, name, bases, namespace, **kwargs)

    def __call__(cls, *args, **kwargs):
        """Create a new instance of the class.

        Notes
        -----
        The formulation is removed from the keyword arguments before the instance is
        created. This is done to prevent the formulation from being passed to the
        ``__init__`` method.
        """
        obj = cls.__new__(cls, *args, **kwargs)
        if "formulation" in kwargs:
            del kwargs["formulation"]
        obj.__init__(*args, **kwargs)
        return obj


class ConnectionMeta(ABCMeta):
    """Metaclass for the :class:`brim.core.model_base.ConnectionBase`."""

    def __new__(mcs, name, bases, namespace, **kwargs):  # noqa: N804
        """Create a new class."""

        def create_submodel_property(requirement: ModelRequirement) -> property:
            def getter(self):
                return getattr(self, f"_get_{requirement.attribute_name}")(self)

            getter.__annotations__ = {"return": requirement.type_hint}
            return property(getter, None, None, requirement.description)

        # Create properties for each of the requirements
        requirements = _get_requirements(bases, namespace, "required_models")
        for req in requirements:
            namespace[req.attribute_name] = create_submodel_property(req)
        namespace["required_models"] = tuple(requirements)  # Update the requirements
        return super().__new__(mcs, name, bases, namespace, **kwargs)


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
        """System object representing the model."""
        return self._system


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

        def conn_not_part_of_model(self):
            raise ValueError(f"The connection {self.name!r} is not part of a model.")

        super().__init__(name)
        for req in self.required_models:
            setattr(self, f"_get_{req.attribute_name}", conn_not_part_of_model)

    def _check_submodel_types(self):
        """Check the types of the submodels.

        Notes
        -----
        This is a helper method which can be called, if there is a hard requirement
        check required. It is not called automatically to allow possible duck typing.
        """
        for req in self.required_models:
            if not isinstance(getattr(self, req.attribute_name), req.types):
                raise TypeError(
                    f"The submodel {req.attribute_name!r} of the connection "
                    f"{self.name!r} should be of type {req.types!r}."
                )

    @abstractmethod
    def define_objects(self) -> None:
        """Define the objects in the connection."""

    @abstractmethod
    def define_kinematics(self) -> None:
        """Define the kinematics of the connection."""

    @abstractmethod
    def define_loads(self) -> None:
        """Define the loads on the connection."""


class ModelBase(BrimBase, metaclass=ModelMeta):
    """Base class for all objects in brim."""

    required_models: tuple[ModelRequirement, ...] = ()
    required_connections: tuple[ConnectionRequirement, ...] = ()

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

    def define_connections(self) -> None:
        """Define the submodels used by connections in the model."""
        for submodel in self.submodels:
            submodel.define_connections()

    @abstractmethod
    def define_objects(self) -> None:
        """Initialize the objects belonging to the model."""
        for submodel in self.submodels:
            submodel.define_objects()

    @abstractmethod
    def define_kinematics(self) -> None:
        """Establish the kinematics of the objects belonging to the model."""
        for submodel in self.submodels:
            submodel.define_kinematics()

    @abstractmethod
    def define_loads(self) -> None:
        """Define the loads that are part of the model."""
        for submodel in self.submodels:
            submodel.define_loads()
