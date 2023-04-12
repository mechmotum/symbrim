"""Module containing the requirement class."""
from __future__ import annotations

from collections.abc import Iterable
from typing import Union

__all__ = ["ModelRequirement", "ConnectionRequirement"]


class RequirementBase:
    """Abstract class to reduce duplication between requirement classes."""

    def __init__(self, attribute_name: str,
                 description: str | None = None,
                 full_name: str | None = None) -> None:
        """Initialize a new instance of the requirement.

        Parameters
        ----------
        attribute_name : str
            Name of the attribute that is used to store the object in the parent.
        description : str, optional
            Description of the object, by default None.
        full_name : str, optional
            Full name of the object, by default capitalized version of the attribute
            name, where the underscores are replaced by spaces.
        """
        attribute_name = str(attribute_name)
        if not attribute_name.isidentifier():
            raise ValueError(f"'{attribute_name}' is not a valid attribute name, "
                             f"because it cannot be used as a variable name.")
        self._attribute_name = attribute_name
        self._description = str(description) if description is not None else ""
        if full_name is None:
            full_name = self.attribute_name.replace("_", " ").capitalize()
        self._full_name = str(full_name)

    @property
    def attribute_name(self) -> str:
        """Name of the attribute that is used to store the object in the parent."""
        return self._attribute_name

    @property
    def description(self) -> str:
        """Description of the object."""
        return self._description

    @property
    def full_name(self) -> str:
        """Full name of the object."""
        return self._full_name

    def __str__(self):
        return self.attribute_name

    def __repr__(self):
        return (f"{self.__class__.__name__}(attribute_name={self.attribute_name!r}, "
                f"description={self.description!r}, full_name={self.full_name!r})")



class ModelRequirement(RequirementBase):
    """Simple class containing the requirement properties."""

    def __init__(self, attribute_name: str,
                 submodel_types: type | tuple[type, ...],
                 description: str | None = None,
                 full_name: str | None = None,
                 type_name: str | None = None) -> None:
        """Initialize a new instance of the requirement.

        Parameters
        ----------
        attribute_name : str
            Name of the attribute that is used to store the submodel in the parent.
        submodel_types : type | tuple[type, ...]
            Supported types of the submodel.
        description : str, optional
            Description of the submodel, by default None.
        full_name : str, optional
            Full name of the submodel, by default capitalized version of the attribute
            name, where the underscores are replaced by spaces.
        type_name : str, optional
            Names of the supported types of the submodel. The names of the type classes
            are used by default.
        """
        super().__init__(attribute_name, description, full_name)
        if not isinstance(submodel_types, Iterable):
            submodel_types = (submodel_types,)
        self._types = tuple(submodel_types)
        if description is None:
            description = self.types[0].__doc__.split("\n", 1)[0]
        self._description = str(description)
        if type_name is None:
            type_name = " or ".join(tp.__name__ for tp in self.types)
        self._type_name = str(type_name)

    @property
    def types(self) -> tuple[type, ...]:
        """Supported types of the submodel."""
        return self._types

    @property
    def type_name(self) -> str:
        """Names of the supported types of the submodel."""
        return self._type_name

    @property
    def type_hint(self) -> type:
        """Type hint for the submodel."""
        return Union[self.types]

    def __repr__(self):
        return (f"{self.__class__.__name__}(attribute_name={self.attribute_name!r}, "
                f"types={self.types!r}, description={self.description!r}, "
                f"full_name={self.full_name!r}, type_name={self.type_name!r})")


class ConnectionRequirement(RequirementBase):
    """Simple class containing the requirement properties."""

    def __init__(self, attribute_name: str,
                 model_references: dict[str, str],
                 description: str | None = None,
                 full_name: str | None = None) -> None:
        """Initialize a new instance of the requirement.

        Parameters
        ----------
        attribute_name : str
            Name of the attribute that is used to store the connection in the parent.
        model_references : dict[str, str]
            Dictionary containing the model references. The keys are the names of the
            attributes in the parent model, and the values are the names of the models
            in the connection.
        description : str, optional
            Description of the connection, by default None.
        full_name : str, optional
            Full name of the connection, by default capitalized version of the
            attribute name, where the underscores are replaced by spaces.
        """
        super().__init__(attribute_name, description, full_name)
        self._model_references = dict(model_references)

    @property
    def model_references(self) -> dict[str, str]:
        """Dictionary containing the model references."""
        return self._model_references

    def __repr__(self):
        return (f"{self.__class__.__name__}(attribute_name={self.attribute_name!r}, "
                f"model_references={self.model_references!r}, "
                f"description={self.description!r}, full_name={self.full_name!r}))")
