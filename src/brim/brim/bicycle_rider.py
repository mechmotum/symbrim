"""Module containing the customizable bicycle-rider model."""
from __future__ import annotations

from sympy.physics.mechanics._system import System

from brim.bicycle import BicycleBase
from brim.brim.base_connections import (
    PedalConnectionBase,
    SeatConnectionBase,
    SteerConnectionBase,
)
from brim.core import ConnectionRequirement, ModelBase, ModelRequirement
from brim.rider import Rider

__all__ = ["BicycleRider"]


class BicycleRider(ModelBase):
    """Model of a bicycle and a rider."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("bicycle", BicycleBase, "Bicycle model."),
        ModelRequirement("rider", Rider, "Rider model."),
    )
    required_connections: tuple[ConnectionRequirement] = (
        ConnectionRequirement(
            "seat_connection", SeatConnectionBase,
            "Connection between the pelvis and the rear frame.", False),
        ConnectionRequirement(
            "pedal_connection", PedalConnectionBase,
            "Connection between the pedals and the legs.", False),
        ConnectionRequirement(
            "steer_connection", SteerConnectionBase,
            "Connection between the steer and the arms.", False),
    )
    bicycle: BicycleBase
    rider: Rider
    seat_connection: SeatConnectionBase
    pedal_connection: PedalConnectionBase
    steer_connection: SteerConnectionBase

    def define_connections(self) -> None:
        """Define the connections."""
        super().define_connections()
        if self.seat_connection is not None:
            self.seat_connection.rear_frame = self.bicycle.rear_frame
            self.seat_connection.pelvis = self.rider.pelvis
        if self.pedal_connection is not None:
            self.pedal_connection.left_leg = self.rider.left_leg
            self.pedal_connection.right_leg = self.rider.right_leg
            self.pedal_connection.pedals = self.bicycle.pedals
        if self.steer_connection is not None:
            self.steer_connection.steer = self.bicycle.front_frame
            self.steer_connection.left_arm = self.rider.left_arm
            self.steer_connection.right_arm = self.rider.right_arm

    def define_objects(self) -> None:
        """Define the objects."""
        super().define_objects()
        self._system = System(self.bicycle.system.origin, self.bicycle.system.frame)
        if self.seat_connection is not None:
            self.seat_connection.define_objects()
        if self.pedal_connection is not None:
            self.pedal_connection.define_objects()
        if self.steer_connection is not None:
            self.steer_connection.define_objects()

    def define_kinematics(self) -> None:
        """Define the kinematics."""
        super().define_kinematics()
        if self.seat_connection is not None:
            self.seat_connection.define_kinematics()
        if self.pedal_connection is not None:
            self.pedal_connection.define_kinematics()
        if self.steer_connection is not None:
            self.steer_connection.define_kinematics()

    def define_loads(self) -> None:
        """Define the loads."""
        super().define_loads()
        if self.seat_connection is not None:
            self.seat_connection.define_loads()
        if self.pedal_connection is not None:
            self.pedal_connection.define_loads()
        if self.steer_connection is not None:
            self.steer_connection.define_loads()

    def define_constraints(self) -> None:
        """Define the constraints."""
        super().define_constraints()
        if self.seat_connection is not None:
            self.seat_connection.define_constraints()
        if self.pedal_connection is not None:
            self.pedal_connection.define_constraints()
        if self.steer_connection is not None:
            self.steer_connection.define_constraints()
