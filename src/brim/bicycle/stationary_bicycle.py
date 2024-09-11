"""Module containing the Whipple bicycle model."""
from __future__ import annotations

from sympy import Matrix, Symbol
from sympy.physics.mechanics import PinJoint, System, dynamicsymbols

from brim.bicycle.bicycle_base import BicycleBase

__all__ = ["StationaryBicycle"]


class StationaryBicycle(BicycleBase):
    """Stationary bicycle model."""

    @property
    def descriptions(self) -> dict[object, str]:
        """Dictionary of descriptions of the Whipple bicycle's attributes."""
        desc = {
            **super().descriptions,
            self.q[0]: f"Rear wheel rotation angle of {self.name}.",
            self.q[1]: f"Steering rotation angle of {self.name}.",
            self.q[2]: f"Front wheel rotation angle of {self.name}.",
            self.symbols["gear_ratio"]: "Ratio between the angle of the rear wheel and"
                                        " the cranks.",
        }
        desc.update({ui: f"Generalized speed of the {desc[qi].lower()}"
                     for qi, ui in zip(self.q, self.u)})
        return desc

    def _define_objects(self) -> None:
        """Define the objects of the Whipple bicycle."""
        super()._define_objects()
        self.q = Matrix(dynamicsymbols(self._add_prefix("q1:4")))
        self.u = Matrix(dynamicsymbols(self._add_prefix("u1:4")))
        self.symbols["gear_ratio"] = Symbol(self._add_prefix("gear_ratio"))
        self._system = System(self.rear_frame.system.frame,
                              self.rear_frame.system.fixed_point)

    def _define_kinematics(self) -> None:
        """Define the kinematics of the Whipple bicycle."""
        super()._define_kinematics()
        # Define the joints
        if self.front_frame:
            self.system.add_joints(
                PinJoint(
                    self._add_prefix("steer_joint"),
                    self.rear_frame.steer_hub.to_valid_joint_arg(),
                    self.front_frame.steer_hub.to_valid_joint_arg(),
                    self.q[1], self.u[1],
                    self.rear_frame.steer_hub.point, self.front_frame.steer_hub.point,
                    self.rear_frame.steer_hub.axis, self.front_frame.steer_hub.axis)
            )
        if self.rear_wheel:
            self.system.add_joints(
                PinJoint(self._add_prefix("rear_wheel_joint"),
                         self.rear_frame.wheel_hub.to_valid_joint_arg(),
                         self.rear_wheel.body, self.q[0], self.u[0],
                         self.rear_frame.wheel_hub.point, self.rear_wheel.center,
                         self.rear_frame.wheel_hub.axis, self.rear_wheel.rotation_axis)
            )
        if self.front_wheel:
            self.system.add_joints(
                PinJoint(self._add_prefix("front_wheel_joint"),
                         self.front_frame.wheel_hub.to_valid_joint_arg(),
                         self.front_wheel.body, self.q[2], self.u[2],
                         self.front_frame.wheel_hub.point, self.front_wheel.center,
                         self.front_frame.wheel_hub.axis,
                         self.front_wheel.rotation_axis),
            )
        if self.cranks:
            self.cranks.center_point.set_pos(self.rear_frame.bottom_bracket, 0)
            self.cranks.frame.orient_axis(
                self.rear_frame.wheel_hub.frame, self.rear_frame.wheel_hub.axis,
                self.q[0] / self.symbols["gear_ratio"])
            self.cranks.frame.set_ang_vel(
                self.rear_frame.wheel_hub.frame,
                self.u[0] / self.symbols["gear_ratio"] * self.rear_frame.wheel_hub.axis)
            if self.q[0] not in self.system.q:
                self.system.add_coordinates(self.q[0])
                self.system.add_speeds(self.u[0])
                self.system.add_kdes(-self.q[0].diff(dynamicsymbols._t) + self.u[0])
