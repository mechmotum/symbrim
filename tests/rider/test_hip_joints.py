from __future__ import annotations

import pytest
from brim.core import ConnectionRequirement, ModelBase, ModelRequirement
from brim.rider.base_connections import HipBase, LeftHipBase, RightHipBase
from brim.rider.hip_joints import (
    PinLeftHip,
    PinRightHip,
    SphericalLeftHip,
    SphericalRightHip,
)
from brim.rider.legs import LegBase, TwoPinStickLeftLeg, TwoPinStickRightLeg
from brim.rider.pelvis import PelvisBase, SimpleRigidPelvis
from brim.utilities.testing import _test_descriptions


class HipModel(ModelBase):
    required_models = (
        ModelRequirement("pelvis", PelvisBase, "Pelvis of the rider."),
        ModelRequirement("leg", LegBase, "Leg of the rider."),
    )
    required_connections = (
        ConnectionRequirement("hip", HipBase, "Hip joint of the rider."),
    )
    pelvis: PelvisBase
    leg: LegBase
    hip: HipBase

    def define_connections(self) -> None:
        self.hip.pelvis = self.pelvis
        self.hip.leg = self.leg

    def define_objects(self) -> None:
        super().define_objects()
        self.hip.define_objects()

    def define_kinematics(self) -> None:
        super().define_kinematics()
        self.hip.define_kinematics()

    def define_loads(self) -> None:
        super().define_loads()
        self.hip.define_loads()


@pytest.mark.parametrize("hip_cls, leg_cls, base_cls", [
    (SphericalLeftHip, TwoPinStickLeftLeg, LeftHipBase),
    (SphericalRightHip, TwoPinStickRightLeg, RightHipBase),
    (PinLeftHip, TwoPinStickLeftLeg, LeftHipBase),
    (PinRightHip, TwoPinStickRightLeg, RightHipBase),
])
class TestHipJointBase:
    def test_types(self, hip_cls, leg_cls, base_cls) -> None:
        hip = hip_cls("hip")
        hip.pelvis = SimpleRigidPelvis("pelvis")
        hip.leg = leg_cls("leg")
        assert isinstance(hip, base_cls)

    def test_descriptions(self, hip_cls, leg_cls, base_cls) -> None:
        hip = hip_cls("hip")
        hip.pelvis = SimpleRigidPelvis("pelvis")
        hip.leg = leg_cls("leg")
        _test_descriptions(hip)


class TestSphericalLeftHipJoint:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = HipModel("model")
        self.model.hip = SphericalLeftHip("hip")
        self.model.pelvis = SimpleRigidPelvis("pelvis")
        self.model.leg = TwoPinStickLeftLeg("leg")
        self.model.define_all()
        self.hip, self.pelvis, self.leg = (
            self.model.hip, self.model.pelvis, self.model.leg)

    def test_kinematics(self):
        w = self.leg.hip_interframe.ang_vel_in(self.pelvis.frame)
        assert w.dot(self.pelvis.y).xreplace(
            {self.hip.q[1]: 0, self.hip.q[2]: 0}) == self.hip.u[0]
        assert w.dot(self.pelvis.x).xreplace(
            {self.hip.q[0]: 0, self.hip.q[2]: 0}) == -self.hip.u[1]
        assert w.dot(self.pelvis.z).xreplace(
            {self.hip.q[0]: 0, self.hip.q[1]: 0}) == self.hip.u[2]


class TestSphericalRightHipJoint:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = HipModel("model")
        self.model.hip = SphericalRightHip("hip")
        self.model.pelvis = SimpleRigidPelvis("pelvis")
        self.model.leg = TwoPinStickRightLeg("leg")
        self.model.define_all()
        self.hip, self.pelvis, self.leg = (
            self.model.hip, self.model.pelvis, self.model.leg)

    def test_kinematics(self):
        w = self.leg.hip_interframe.ang_vel_in(self.pelvis.frame)
        assert w.dot(self.pelvis.y).xreplace(
            {self.hip.q[1]: 0, self.hip.q[2]: 0}) == self.hip.u[0]
        assert w.dot(self.pelvis.x).xreplace(
            {self.hip.q[0]: 0, self.hip.q[2]: 0}) == self.hip.u[1]
        assert w.dot(self.pelvis.z).xreplace(
            {self.hip.q[0]: 0, self.hip.q[1]: 0}) == self.hip.u[2]


@pytest.mark.parametrize("hip_cls, leg_cls", [
    (PinLeftHip, TwoPinStickLeftLeg), (PinRightHip, TwoPinStickRightLeg)])
class TestPinLeftHipJoint:
    @pytest.fixture(autouse=True)
    def _setup(self, hip_cls, leg_cls) -> None:
        self.model = HipModel("model")
        self.model.hip = hip_cls("hip")
        self.model.pelvis = SimpleRigidPelvis("pelvis")
        self.model.leg = leg_cls("leg")
        self.model.define_all()
        self.hip, self.pelvis, self.leg = (
            self.model.hip, self.model.pelvis, self.model.leg)

    def test_kinematics(self):
        w = self.leg.hip_interframe.ang_vel_in(self.pelvis.frame)
        assert w.dot(self.pelvis.y) == self.hip.u
