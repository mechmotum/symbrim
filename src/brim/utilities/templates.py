"""Module containing templates for creating new models.

Explanation
-----------
BRiM uses the concept that a model consists out of other models, between which there are
certain interactions. A bicycle consists out of a rear wheel, a front wheel, a rear
frame, a front frame and a ground. Each of these components, called submodels, are a
system on its own. The bicycle takes these different submodels and connects them. The
rear frame is connected to the rear wheel, the front frame to the front wheel, etc.

To make sure that every relation is defined on time, i.e. before it is used, a model
breaks up the definition of its system in multiple parts:

- ``define_objects``: define the objects of the model, like the points, the frames, the
  bodies, etc. The system is often also initiated in this phase. This method is called
  when a model is initiated.
- ``define_kinematics``: define the kinematics of the model, like the position of the
  points, the velocity of the bodies, etc.
- ``define_loads``: define the loads on the model, like the forces and torques acting
  within the system. It has been decided to currently also define the constraints in
  this phase. This may however change in the future.

When calling one of those methods, the model will automatically first call the same
method for all the submodels, before actually defining the system of the current model.
This way, the system of the current model can be defined in terms of the submodels.

Notes
-----
These templates are not meant to be used directly, but rather as a guideline for
creating new models. They are however used in the tests to test the functionality of
the base classes.

"""
from __future__ import annotations

from abc import abstractmethod
from typing import Any

from sympy import Matrix
from sympy.physics.mechanics import dynamicsymbols
from sympy.physics.mechanics.system import System

from brim.core import (
    ModelBase,
    ModelRequirement,
    NewtonianBodyMixin,
)

__all__ = ["MySubModelBase", "MySubModel", "MyModel"]


class MySubModelBase(NewtonianBodyMixin, ModelBase):
    """Template of a submodel base class, like :class:`brim.wheels.WheelBase`.

    Explanation
    -----------
    A base class of a model is generally used to define how a certain category of models
    should look like. In case of :class:`brim.wheels.WheelBase` it is known that a wheel
    should have a ``body``, a ``rotation_axis`` and so on. Therefore, the
    :class:`brim.wheels.WheelBase` creates the abstract methods for those, such that
    classes which can use a wheel know that it has those properties. The use of a
    prescibed method like ``rotation_axis`` is that the parent model can use it to
    orient the wheel with respect to the frame using a rotation about ``rotation_axis``.

    In this template class we prescribe that is has a body and that subclasses should
    also implement a method called ``my_submodel_method``, which can be used by the
    parent model. As many models will actually use a Newtonian body with respect to
    which the model is defined, a mixin :class:`brim.core.NewtonianBodyMixin` has been
    implemented. This mixin will create some useful properties associated with a body,
    such as ``body`` and ``frame``.

    As this is is a base class, it does not have to implement all abstract methods from
    :class:`brim.ModelBase`.

    See Also
    --------
    :class:`brim.templates.MySubModel` is a subclass of this base class.

    """

    @abstractmethod
    def my_submodel_method(self, variable: ModelBase) -> None:
        """Abstract method that should be implemented by subclasses.

        Explanation
        -----------
        A method like this can be useful for creating an interface for a parent model to
        define an interaction with a different submodel. An example in brim is
        :meth:`brim.bicycle.wheels.compute_contact_point` which needs the ground model
        to compute the contact point of the wheel. As the ground model is not known by
        the wheel model, the parent model,
        :class:`brim.bicycle.whipple_bicycle.WhippleBicycle`, calls this method
        providing the ground to define the location of the contact point.

        Parameters
        ----------
        variable : ModelBase
            Explanation about what this variable is.

        """


class MySubModel(MySubModelBase):
    """Template of a submodel, like :class:`brim.wheels.KnifeEdgeWheel`.

    Explanation
    -----------
    As this sub model inherits from :class:`brim.templates.MySubModelBase`, it has to
    implement the abstract methods ``my_submodel_method`` and ``define_kinematics``,
    ``define_loads``. The latter two are defined as abstract methods in
    :class:`brim.core.model_base.ModelBase`. Of course we can also add additional
    methods and properties. In this case we add a symbolic variable ``my_symbol``,
    including a description of what it is in the the ``descriptions`` property.

    """

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the model."""
        return {self.my_symbol: f"Symbolic variable of {self.name}"}

    def define_objects(self) -> None:
        """Define the objects of the model."""
        super().define_objects()
        # _add_prefix adds the name of the model to the variable, such that it is unique
        # in the system.
        self.my_symbol = dynamicsymbols(self._add_prefix("my_symbol"))

    def define_kinematics(self) -> None:
        """Define the kinematics of the model."""
        super().define_kinematics()

    def define_loads(self) -> None:
        """Define the loads of the model."""
        super().define_loads()

    def my_submodel_method(self, variable: ModelBase) -> None:
        """Implementat the prescribed abstract method."""


class MyModel(ModelBase):
    """Template of a model.

    Explanation
    -----------
    A normal model can also directly inherit from
    :class:`brim.core.model_base.ModelBase` and implement all abstract methods required
    for initialization:

    - ``system``: a :class:`sympy.physics.mechanics.system.System` instance, which does
      the book-keeping of the objects and relations from this models perspective. This
      means that it should not contain all objects known to the submodels. Just the ones
      necessary to describe the relationships governed by this model.
    - ``define_objects``: initializes the objects belonging to the model and also puts
      them in ``system`` if possible.
    - ``define_kinematics``: defines the kinematics of the model and mainly between the
      different submodels, as the kinematics within the submodels gets defined by the
      submodels themselves.
    - ``define_loads``: defines the loads act upon the model and again mainly the ones
      between the submodels.

    Additional methods that can be useful to specify are:
    - ``required_models`` which is a property, which mentions the required submodels.
      This property is parsed on initialization, such that the class automatically gets
      a property for each of these required_models.
    - ``descriptions`` is a dictionary with descriptions of all the model associated
      objects, which don't have a docstring. This is mainly useful for explaining the
      meaning of symbols.

    In this implementation we create two hard required_models, namely ``submodel1`` and
    ``submodel2``. These submodels are required to be subclasses of
    :class:`brim.utilities.templates.MySubModelBase`. In this example we orient
    ``submodel2`` with a body-fixed rotation with respect to ``submodel1``.

    """

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("submodel1", MySubModelBase, "Description of submodel1", True),
        ModelRequirement("submodel2", MySubModelBase, "Description of submodel2", True),
    )
    # Adding annotations for IDEs
    submodel1: MySubModelBase
    submodel2: MySubModelBase

    @property
    def system(self) -> System:
        """System object representing the model."""
        return self._system

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the model."""
        return {
            self.q[0]: f"Yaw angle between {self.submodel1} and {self.submodel2}.",
            self.q[1]: f"Roll angle between {self.submodel1} and {self.submodel2}.",
            self.q[2]: f"Pitch angle between {self.submodel1} and {self.submodel2}.",
        }

    def define_objects(self) -> None:
        """Initialize the objects belonging to the model."""
        super().define_objects()
        self.q = Matrix(dynamicsymbols("q1:4"))
        self._system = None

    def define_kinematics(self) -> None:
        """Establish the kinematics of the objects belonging to the model."""
        super().define_kinematics()
        self._system = System(self.submodel1.body.masscenter, self.submodel1.frame)
        self.submodel2.frame.orient_body_fixed(self.submodel1.frame, self.q[:], "zxy")

    def define_loads(self) -> None:
        """Define the loads that are part of the model."""
        super().define_loads()
        # One can for example use self.submodel1.my_submodel_method here
