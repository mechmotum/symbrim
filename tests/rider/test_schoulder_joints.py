from __future__ import annotations

import pytest
from brim.core import ConnectionRequirement, ModelBase, ModelRequirement
from brim.rider.arms import ArmBase, PinElbowStickLeftArm, PinElbowStickRightArm
from brim.rider.base_connections import (
    LeftShoulderBase,
    RightShoulderBase,
    ShoulderBase,
)
from brim.rider.shoulder_joints import SphericalLeftShoulder, SphericalRightShoulder
from brim.rider.torso import SimpleRigidTorso, TorsoBase
from brim.utilities.testing import _test_descriptions


class ShoulderModel(ModelBase):
    required_models = (
        ModelRequirement("torso", TorsoBase, "Torso of the rider."),
        ModelRequirement("arm", ArmBase, "Arm of the rider."),
    )
    required_connections = (
        ConnectionRequirement("shoulder", ShoulderBase,
                              "Shoulder joint of the rider."),
    )
    torso: TorsoBase
    arm: ArmBase
    shoulder: ShoulderBase

    def define_connections(self) -> None:
        self.shoulder.torso = self.torso
        self.shoulder.arm = self.arm

    def define_objects(self) -> None:
        super().define_objects()
        self.shoulder.define_objects()

    def define_kinematics(self) -> None:
        super().define_kinematics()
        self.shoulder.define_kinematics()

    def define_loads(self) -> None:
        super().define_loads()
        self.shoulder.define_loads()


@pytest.mark.parametrize("shoulder_cls, arm_cls, base_cls", [
    (SphericalLeftShoulder, PinElbowStickLeftArm, LeftShoulderBase),
    (SphericalRightShoulder, PinElbowStickRightArm, RightShoulderBase),
])
class TestShoulderJointBase:
    def test_types(self, shoulder_cls, arm_cls, base_cls) -> None:
        shoulder = shoulder_cls("shoulder")
        shoulder.torso = SimpleRigidTorso("torso")
        shoulder.arm = arm_cls("arm")
        assert isinstance(shoulder, base_cls)

    def test_descriptions(self, shoulder_cls, arm_cls, base_cls) -> None:
        shoulder = shoulder_cls("shoulder")
        shoulder.torso = SimpleRigidTorso("torso")
        shoulder.arm = arm_cls("arm")
        _test_descriptions(shoulder)


class TestSphericalLeftShoulderJoint:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = ShoulderModel("model")
        self.model.shoulder = SphericalLeftShoulder("shoulder")
        self.model.torso = SimpleRigidTorso("torso")
        self.model.arm = PinElbowStickLeftArm("arm")
        self.model.define_all()
        self.shoulder, self.torso, self.arm = (
            self.model.shoulder, self.model.torso, self.model.arm)

    def test_kinematics(self) -> None:
        w = self.arm.upper_arm.frame.ang_vel_in(self.torso.frame)
        assert w.dot(self.torso.y).xreplace(
            {self.shoulder.q[1]: 0, self.shoulder.q[2]: 0}) == self.shoulder.u[0]
        assert w.dot(self.torso.x).xreplace(
            {self.shoulder.q[0]: 0, self.shoulder.q[2]: 0}) == -self.shoulder.u[1]
        assert w.dot(self.torso.z).xreplace(
            {self.shoulder.q[0]: 0, self.shoulder.q[1]: 0}) == self.shoulder.u[2]


class TestSphericalRightShoulderJoint:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = ShoulderModel("model")
        self.model.shoulder = SphericalRightShoulder("shoulder")
        self.model.torso = SimpleRigidTorso("torso")
        self.model.arm = PinElbowStickRightArm("arm")
        self.model.define_all()
        self.shoulder, self.torso, self.arm = (
            self.model.shoulder, self.model.torso, self.model.arm)

    def test_kinematics(self) -> None:
        w = self.arm.upper_arm.frame.ang_vel_in(self.torso.frame)
        assert w.dot(self.torso.y).xreplace(
            {self.shoulder.q[1]: 0, self.shoulder.q[2]: 0}) == self.shoulder.u[0]
        assert w.dot(self.torso.x).xreplace(
            {self.shoulder.q[0]: 0, self.shoulder.q[2]: 0}) == self.shoulder.u[1]
        assert w.dot(self.torso.z).xreplace(
            {self.shoulder.q[0]: 0, self.shoulder.q[1]: 0}) == self.shoulder.u[2]
