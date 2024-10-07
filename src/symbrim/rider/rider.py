"""Module containing the customizable rider models."""
from __future__ import annotations

from sympy.physics.mechanics import System

from symbrim.core import ConnectionRequirement, ModelBase, ModelRequirement
from symbrim.rider.arms import LeftArmBase, RightArmBase
from symbrim.rider.base_connections import (
    LeftHipBase,
    LeftShoulderBase,
    RightHipBase,
    RightShoulderBase,
    SacrumBase,
)
from symbrim.rider.legs import LeftLegBase, RightLegBase
from symbrim.rider.pelvis import PelvisBase
from symbrim.rider.torso import TorsoBase

__all__ = ["Rider"]


class Rider(ModelBase):
    """Customizable rider mode."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("pelvis", PelvisBase, "Pelvis of the rider."),
        ModelRequirement("torso", TorsoBase, "Torso of the rider.", False),
        ModelRequirement("left_arm", LeftArmBase, "Left arm of the rider.", False),
        ModelRequirement("right_arm", RightArmBase, "Right arm of the rider.", False),
        ModelRequirement("left_leg", LeftLegBase, "Left leg of the rider.", False),
        ModelRequirement("right_leg", RightLegBase, "Right leg of the rider.", False),
    )
    required_connections: tuple[ConnectionRequirement] = (
        ConnectionRequirement("sacrum", SacrumBase,
                              "Connection between the pelvis and the torso.", False),
        ConnectionRequirement("left_shoulder", LeftShoulderBase,
                              "Connection between the torso and the left arm.", False),
        ConnectionRequirement("right_shoulder", RightShoulderBase,
                              "Connection between the torso and the right arm.", False),
        ConnectionRequirement("left_hip", LeftHipBase,
                              "Connection between the pelvis and the left leg.", False),
        ConnectionRequirement("right_hip", RightHipBase,
                              "Connection between the pelvis and the right leg.", False)
    )
    pelvis: PelvisBase
    torso: TorsoBase
    left_arm: LeftArmBase
    right_arm: RightArmBase
    left_leg: LeftLegBase
    right_leg: RightLegBase
    sacrum: SacrumBase
    left_shoulder: LeftShoulderBase
    right_shoulder: RightShoulderBase
    left_hip: LeftHipBase
    right_hip: RightHipBase

    def _define_connections(self) -> None:
        """Define the connections."""
        super()._define_connections()
        if self.sacrum:
            self.sacrum.pelvis = self.pelvis
            self.sacrum.torso = self.torso
        if self.left_shoulder:
            self.left_shoulder.torso = self.torso
            self.left_shoulder.arm = self.left_arm
        if self.right_shoulder:
            self.right_shoulder.torso = self.torso
            self.right_shoulder.arm = self.right_arm
        if self.left_hip:
            self.left_hip.pelvis = self.pelvis
            self.left_hip.leg = self.left_leg
        if self.right_hip:
            self.right_hip.pelvis = self.pelvis
            self.right_hip.leg = self.right_leg

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self._system = System.from_newtonian(self.pelvis.body)
        for conn in self.connections:
            conn.define_objects()

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        for conn in self.connections:
            conn.define_kinematics()

    def _define_loads(self) -> None:
        """Define the loads."""
        super()._define_loads()
        for conn in self.connections:
            conn.define_loads()

    def _define_constraints(self) -> None:
        """Define the constraints."""
        super()._define_constraints()
        for conn in self.connections:
            conn.define_constraints()
