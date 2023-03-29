"""Module containing the Whipple bicycle model."""
from __future__ import annotations

from typing import Any

from sympy import Matrix
from sympy.physics.mechanics import PinJoint, System, dynamicsymbols

from brim.bicycle.bicycle_base import BicycleBase
from brim.bicycle.front_frames import FrontFrameBase
from brim.bicycle.grounds import GroundBase
from brim.bicycle.rear_frames import RearFrameBase
from brim.bicycle.wheels import WheelBase
from brim.core import Requirement

__all__ = ["WhippleBicycle", "WhippleBicycleMoore"]


class WhippleBicycle(BicycleBase):
    """Base class for the Whipple bicycle model."""

    requirements: tuple[Requirement, ...] = (
        Requirement("ground", GroundBase, "Submodel of the ground.", True),
        Requirement("rear_frame", RearFrameBase, "Submodel of the rear frame.", True),
        Requirement("front_frame", FrontFrameBase, "Submodel of the front frame.",
                    True),
        Requirement("rear_wheel", WheelBase, "Submodel of the rear wheel.", True),
        Requirement("front_wheel", WheelBase, "Submodel of the front wheel.", True),
    )
    ground: GroundBase
    rear_frame: RearFrameBase
    front_frame: FrontFrameBase
    rear_wheel: WheelBase
    front_wheel: WheelBase

    def __new__(cls, name: str, *args, formulation: str = "moore", **kwargs
                ) -> WhippleBicycle:
        """Create a new instance of the Whipple bicycle.

        Parameters
        ----------
        name : str
            Name of the Whipple bicycle.
        formulation : str, optional
            Formulation of the Whipple bicycle, by default "moore".

        """
        if formulation == "moore":
            cls = WhippleBicycleMoore
        else:
            raise NotImplementedError(f"The formulation '{formulation}' has not "
                                      f"been implemented in {cls}.")
        return super().__new__(cls)


class WhippleBicycleMoore(WhippleBicycle):
    """Whipple bicycle model based on Moore's formulation."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Dictionary of descriptions of the Whipple bicycle's attributes."""
        desc = {
            **super().descriptions,
            self.q[0]: "Perpendicular distance along ground.x to the rear contact point"
                       " in the ground plane.",
            self.q[1]: "Perpendicular distance along ground.y to the rear contact point"
                       " in the ground plane.",
            self.q[2]: "Yaw angle of the rear frame.",
            self.q[3]: "Roll angle of the rear frame.",
            self.q[4]: "Pitch angle of the rear frame.",
            self.q[5]: "Front wheel rotation angle.",
            self.q[6]: "Steering rotation angle.",
            self.q[7]: "Rear wheel rotation angle.",
        }
        desc.update({ui: f"Generalized speed of the {desc[qi].lower()}"
                     for qi, ui in zip(self.q, self.u)})
        return desc

    def define_objects(self) -> None:
        """Define the objects of the Whipple bicycle."""
        self.q = Matrix(dynamicsymbols(self.add_prefix("q1:9")))
        self.u = Matrix(dynamicsymbols(self.add_prefix("u1:9")))

    def define_kinematics(self) -> None:
        """Define the kinematics of the Whipple bicycle."""
        self._system = System.from_newtonian(self.ground.body)
        # Define the location of the rear wheel contact point in the ground frame.
        self.rear_wheel.contact_point.set_pos(
            self.ground.origin,
            self.q[0] * self.ground.planar_vectors[0] +
            self.q[1] * self.ground.planar_vectors[1])
        self.rear_wheel.contact_point.set_vel(
            self.ground.frame,
            self.u[0] * self.ground.planar_vectors[0] +
            self.u[1] * self.ground.planar_vectors[1])
        # Define the orientation of the rear frame.
        self.rear_frame.frame.orient_body_fixed(self.ground.frame, self.q[2:5], "zxy")
        self.rear_frame.frame.set_ang_vel(
            self.ground.frame,
            self.rear_frame.frame.ang_vel_in(self.ground.frame).xreplace(
                {qi.diff(dynamicsymbols._t): ui for qi, ui in zip(self.q, self.u)}))
        # Define the joints
        self.system.add_joints(
            PinJoint(self.add_prefix("rear_wheel_joint"), self.rear_frame.body,
                     self.rear_wheel.body, self.q[5], self.u[5],
                     self.rear_frame.wheel_attachment, self.rear_wheel.center,
                     self.rear_frame.wheel_axis, self.rear_wheel.rotation_axis),
            PinJoint(self.add_prefix("steer_joint"), self.rear_frame.body,
                     self.front_frame.body, self.q[6], self.u[6],
                     self.rear_frame.steer_attachment,
                     self.front_frame.steer_attachment, self.rear_frame.steer_axis,
                     self.front_frame.steer_axis),
            PinJoint(self.add_prefix("front_wheel_joint"), self.front_frame.body,
                     self.front_wheel.body, self.q[7], self.u[7],
                     self.front_frame.wheel_attachment, self.front_wheel.center,
                     self.front_frame.wheel_axis, self.front_wheel.rotation_axis),
        )
        # Define contact points.
        self.rear_wheel.compute_contact_point(self.ground)
        self.front_wheel.compute_contact_point(self.ground)
        # Add the coordinates and speeds to the system.
        self.system.add_coordinates(*self.q[:5])
        self.system.add_speeds(*self.u[:5])
        self.system.add_kdes(*(
            ui - qi.diff(dynamicsymbols._t) for qi, ui in zip(self.q[:5], self.u[:5])))

    def define_loads(self) -> None:
        """Define the loads of the Whipple bicycle."""
        self.rear_wheel.compute_tyre_model(self.ground, True)
        self.front_wheel.compute_tyre_model(self.ground, False)

    @property
    def system(self) -> System:
        """System of the Whipple bicycle."""
        return self._system
