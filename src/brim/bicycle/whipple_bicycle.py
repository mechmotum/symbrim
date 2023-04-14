"""Module containing the Whipple bicycle model."""
from __future__ import annotations

from typing import Any

from sympy import Matrix
from sympy.physics.mechanics import PinJoint, System, dynamicsymbols

from brim.bicycle.bicycle_base import BicycleBase
from brim.bicycle.front_frames import FrontFrameBase
from brim.bicycle.grounds import GroundBase
from brim.bicycle.rear_frames import RearFrameBase
from brim.bicycle.tyre_models import TyreModelBase
from brim.bicycle.wheels import WheelBase
from brim.core import ConnectionRequirement, ModelRequirement, set_default_formulation

__all__ = ["WhippleBicycle", "WhippleBicycleMoore"]


@set_default_formulation("moore")
class WhippleBicycle(BicycleBase):
    """Base class for the Whipple bicycle model."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("ground", GroundBase, "Submodel of the ground."),
        ModelRequirement("rear_frame", RearFrameBase, "Submodel of the rear frame."),
        ModelRequirement("front_frame", FrontFrameBase, "Submodel of the front frame."),
        ModelRequirement("rear_wheel", WheelBase, "Submodel of the rear wheel."),
        ModelRequirement("front_wheel", WheelBase, "Submodel of the front wheel."),
    )
    required_connections: tuple[ConnectionRequirement, ...] = (
        ConnectionRequirement("rear_tyre", TyreModelBase,
                              "Tyre model for the rear wheel."),
        ConnectionRequirement("front_tyre", TyreModelBase,
                              "Tyre model for the front wheel."),
    )
    ground: GroundBase
    rear_frame: RearFrameBase
    front_frame: FrontFrameBase
    rear_wheel: WheelBase
    front_wheel: WheelBase
    rear_tyre: TyreModelBase
    front_tyre: TyreModelBase

    def define_connections(self) -> None:
        """Define the connections between the submodels."""
        super().define_connections()
        self.rear_tyre.ground = self.ground
        self.rear_tyre.wheel = self.rear_wheel
        self.front_tyre.ground = self.ground
        self.front_tyre.wheel = self.front_wheel


class WhippleBicycleMoore(WhippleBicycle):
    """Whipple bicycle model based on Moore's formulation."""

    formulation: str = "moore"

    @property
    def descriptions(self) -> dict[Any, str]:
        """Dictionary of descriptions of the Whipple bicycle's attributes."""
        desc = {
            **super().descriptions,
            self.q[0]: f"Perpendicular distance along ground.x to the rear contact "
                       f"point in the ground plane of {self.name}.",
            self.q[1]: f"Perpendicular distance along ground.y to the rear contact "
                       f"point in the ground plane of {self.name}.",
            self.q[2]: f"Yaw angle of the rear frame of {self.name}.",
            self.q[3]: f"Roll angle of the rear frame of {self.name}.",
            self.q[4]: f"Pitch angle of the rear frame of {self.name}.",
            self.q[5]: f"Front wheel rotation angle of {self.name}.",
            self.q[6]: f"Steering rotation angle of {self.name}.",
            self.q[7]: f"Rear wheel rotation angle of {self.name}.",
        }
        desc.update({ui: f"Generalized speed of the {desc[qi].lower()}"
                     for qi, ui in zip(self.q, self.u)})
        return desc

    def define_objects(self) -> None:
        """Define the objects of the Whipple bicycle."""
        super().define_objects()
        self.rear_tyre.define_objects()
        self.rear_tyre.on_ground = True
        self.front_tyre.define_objects()
        self.q: Matrix = Matrix(dynamicsymbols(self._add_prefix("q1:9")))
        self.u: Matrix = Matrix(dynamicsymbols(self._add_prefix("u1:9")))

    def define_kinematics(self) -> None:
        """Define the kinematics of the Whipple bicycle."""
        super().define_kinematics()
        self._system = System.from_newtonian(self.ground.body)
        # Define the location of the rear wheel contact point in the ground frame.
        self.rear_tyre.contact_point.set_pos(
            self.ground.origin,
            self.q[0] * self.ground.planar_vectors[0] +
            self.q[1] * self.ground.planar_vectors[1])
        self.rear_tyre.contact_point.set_vel(
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
            PinJoint(self._add_prefix("rear_wheel_joint"), self.rear_frame.body,
                     self.rear_wheel.body, self.q[5], self.u[5],
                     self.rear_frame.wheel_attachment, self.rear_wheel.center,
                     self.rear_frame.wheel_axis, self.rear_wheel.rotation_axis),
            PinJoint(self._add_prefix("steer_joint"), self.rear_frame.body,
                     self.front_frame.body, self.q[6], self.u[6],
                     self.rear_frame.steer_attachment,
                     self.front_frame.steer_attachment, self.rear_frame.steer_axis,
                     self.front_frame.steer_axis),
            PinJoint(self._add_prefix("front_wheel_joint"), self.front_frame.body,
                     self.front_wheel.body, self.q[7], self.u[7],
                     self.front_frame.wheel_attachment, self.front_wheel.center,
                     self.front_frame.wheel_axis, self.front_wheel.rotation_axis),
        )
        # Define contact points.
        self.rear_tyre.define_kinematics()
        self.front_tyre.define_kinematics()
        # Add the coordinates and speeds to the system.
        self.system.add_coordinates(*self.q[:5])
        self.system.add_speeds(*self.u[:5])
        self.system.add_kdes(*(
            ui - qi.diff(dynamicsymbols._t) for qi, ui in zip(self.q[:5], self.u[:5])))

    def define_loads(self) -> None:
        """Define the loads of the Whipple bicycle."""
        super().define_loads()
        self.rear_tyre.define_loads()
        self.front_tyre.define_loads()

    def define_constraints(self) -> None:
        """Define the constraints of the Whipple bicycle."""
        super().define_constraints()
        self.rear_tyre.define_constraints()
        self.front_tyre.define_constraints()
