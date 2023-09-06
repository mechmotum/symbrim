"""Module for joint attachments."""

from sympy import Expr, S
from sympy.physics.mechanics import (
    Dyadic,
    Inertia,
    Point,
    ReferenceFrame,
    RigidBody,
    Vector,
)

__all__ = ["Attachment", "Hub", "MasslessBody"]


class MasslessBody(RigidBody):
    """Massless rigid body.

    Explanation
    -----------
    The main purpose of this class is to allow the usage of just a frame and point
    when defining a joint. This class should only be used as long as sympy's joints
    framework does not yet support passing only a frame and point to the joint
    constructor.
    """

    def __init__(self, name: str, masscenter: Point, frame: ReferenceFrame) -> None:
        """Initialize a massless body."""
        super().__init__(
            name, masscenter, frame, S.Zero, Inertia(masscenter, Dyadic(0)))

    @RigidBody.mass.setter
    def mass(self, mass: Expr) -> None:
        """Body's mass."""
        if mass != 0:
            raise AttributeError("Massless bodies must have zero mass.")
        RigidBody.mass.fset(self, mass)

    @RigidBody.inertia.setter
    def inertia(self, inertia: Inertia) -> None:
        """Body's inertia about a point; stored as (Dyadic, Point)."""
        if inertia[0] != Dyadic(0):
            raise AttributeError("Massless bodies do not have inertia.")
        RigidBody.inertia.fset(self, inertia)

    @RigidBody.potential_energy.setter
    def potential_energy(self, potential_energy: Expr) -> None:
        """Potential energy of the body."""
        if potential_energy != 0:
            raise AttributeError("Massless bodies do not have potential energy.")
        RigidBody.potential_energy.fset(self, potential_energy)

    def linear_momentum(self, frame: ReferenceFrame) -> Vector:
        """Linear momentum of the body."""
        return Vector(0)

    def angular_momentum(self, point: Point, frame: ReferenceFrame) -> Vector:
        """Angular momentum of the body about a point in a frame."""
        return Vector(0)

    def kinetic_energy(self, frame: ReferenceFrame) -> Expr:
        """Kinetic energy of the body."""
        return S.Zero


class Attachment:
    """Joint attachment.

    Explanation
    -----------
    This class holds an immutable reference to a reference frame and a point to be used
    in SymPy's joints framework.
    """

    def __init__(self, frame: ReferenceFrame, point: Point) -> None:
        if not isinstance(frame, ReferenceFrame):
            raise TypeError("Frame must be a ReferenceFrame.")
        if not isinstance(point, Point):
            raise TypeError("Point must be a Point.")
        self._frame = frame
        self._point = point
        self.point.set_vel(self.frame, 0)

    @classmethod
    def from_name(cls, name: str) -> "Attachment":
        """Create an attachment based on a name."""
        name = str(name)
        if not name.isidentifier():
            raise ValueError("Name must be a valid identifier.")
        return cls(ReferenceFrame(f"{name}_frame"), Point(f"{name}_point"))

    @property
    def frame(self) -> ReferenceFrame:
        """Reference frame of the attachment."""
        return self._frame

    @property
    def point(self) -> Point:
        """Point of the attachment."""
        return self._point

    def to_valid_joint_arg(self, name: str | None = None) -> MasslessBody:
        """Convert the attachment to a massless body.

        Explanation
        -----------
        This method is used to convert an attachment to a massless body. This is
        necessary because sympy's joints framework does not yet support passing only a
        frame and point to the joint constructor. Therefore, this method may be removed
        once this functionality is added to sympy.
        """
        if name is None:
            name = "massless_body"
        return MasslessBody(name, self.point, self.frame)

    def __getitem__(self, item):
        return (self.frame, self.point)[item]


class Hub(Attachment):
    """Joint attachment for pin joints.

    Explanation
    -----------
    This class is used to define the attachment points of pin joints. It extends
    :class:`brim.core.attachment.Attachment` by specifying an additional rotation axis
    property.
    """

    def __init__(self, frame: ReferenceFrame, point: Point, axis: str | Vector) -> None:
        super().__init__(frame, point)
        if isinstance(axis, str):
            times = 1
            if axis.startswith("-"):
                times = -1
                axis = axis[1:]
            elif axis.startswith("+"):
                axis = axis[1:]
            if axis not in "xyz":
                raise ValueError("Rotation axis must be 'x', 'y' or 'z'.")
            axis = times * self.frame[axis]
        if not isinstance(axis, Vector):
            raise TypeError("Axis must be a Vector.")
        self._axis = axis

    @classmethod
    def from_name(cls, name: str, axis: str) -> "Hub":
        """Create a hub based on a name and an axis."""
        name = str(name)
        if not name.isidentifier():
            raise ValueError("Name must be a valid identifier.")
        return cls(ReferenceFrame(f"{name}_frame"), Point(f"{name}_point"), axis)

    @property
    def axis(self) -> Vector:
        """Rotation axis of the hub."""
        return self._axis
