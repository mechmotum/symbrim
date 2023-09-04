"""Module containing the customizable bicycle-rider model."""
from __future__ import annotations

from sympy.physics.mechanics._system import System

from brim.bicycle import BicycleBase
from brim.brim.base_connections import (
    HandGripsBase,
    PedalsBase,
    SeatBase,
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
            "seat", SeatBase,
            "Connection between the pelvis and the rear frame.", False),
        ConnectionRequirement(
            "pedals", PedalsBase,
            "Connection between the cranks and the legs.", False),
        ConnectionRequirement(
            "hand_grips", HandGripsBase,
            "Connection between the steer and the arms.", False),
    )
    bicycle: BicycleBase
    rider: Rider
    seat: SeatBase
    pedals: PedalsBase
    hand_grips: HandGripsBase

    def _define_connections(self) -> None:
        """Define the connections."""
        super()._define_connections()
        if self.seat is not None:
            self.seat.rear_frame = self.bicycle.rear_frame
            self.seat.pelvis = self.rider.pelvis
        if self.pedals is not None:
            self.pedals.left_leg = self.rider.left_leg
            self.pedals.right_leg = self.rider.right_leg
            self.pedals.cranks = self.bicycle.cranks
        if self.hand_grips is not None:
            self.hand_grips.steer = self.bicycle.front_frame
            self.hand_grips.left_arm = self.rider.left_arm
            self.hand_grips.right_arm = self.rider.right_arm

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self._system = System(self.bicycle.system.frame, self.bicycle.system.origin)
        if self.seat is not None:
            self.seat.define_objects()
        if self.pedals is not None:
            self.pedals.define_objects()
        if self.hand_grips is not None:
            self.hand_grips.define_objects()

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        if self.seat is not None:
            self.seat.define_kinematics()
        if self.pedals is not None:
            self.pedals.define_kinematics()
        if self.hand_grips is not None:
            self.hand_grips.define_kinematics()

    def _define_loads(self) -> None:
        """Define the loads."""
        super()._define_loads()
        if self.seat is not None:
            self.seat.define_loads()
        if self.pedals is not None:
            self.pedals.define_loads()
        if self.hand_grips is not None:
            self.hand_grips.define_loads()

    def _define_constraints(self) -> None:
        """Define the constraints."""
        super()._define_constraints()
        if self.seat is not None:
            self.seat.define_constraints()
        if self.pedals is not None:
            self.pedals.define_constraints()
        if self.hand_grips is not None:
            self.hand_grips.define_constraints()
