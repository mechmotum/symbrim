from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from brim.core import ConnectionRequirement, ModelBase, ModelRequirement
from brim.rider.base_connections import HipBase, LeftHipBase, RightHipBase
from brim.rider.hip_joints import (
    PinLeftHip,
    PinRightHip,
    SphericalHipTorque,
    SphericalLeftHip,
    SphericalRightHip,
)
from brim.rider.legs import LegBase, TwoPinStickLeftLeg, TwoPinStickRightLeg
from brim.rider.pelvis import PelvisBase, PlanarPelvis
from brim.utilities.testing import _test_descriptions
from brim.utilities.utilities import check_zero

if TYPE_CHECKING:
    from sympy.physics.mechanics._system import System


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

    @property
    def system(self) -> System | None:
        return self.hip.system

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
        hip.pelvis = PlanarPelvis("pelvis")
        hip.leg = leg_cls("leg")
        assert isinstance(hip, base_cls)

    def test_descriptions(self, hip_cls, leg_cls, base_cls) -> None:
        hip = hip_cls("hip")
        hip.pelvis = PlanarPelvis("pelvis")
        hip.leg = leg_cls("leg")
        _test_descriptions(hip)


class TestSphericalLeftHipJoint:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = HipModel("model")
        self.model.hip = SphericalLeftHip("hip")
        self.model.pelvis = PlanarPelvis("pelvis")
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
        self.model.pelvis = PlanarPelvis("pelvis")
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
        self.model.pelvis = PlanarPelvis("pelvis")
        self.model.leg = leg_cls("leg")
        self.model.define_all()
        self.hip, self.pelvis, self.leg = (
            self.model.hip, self.model.pelvis, self.model.leg)

    def test_kinematics(self):
        w = self.leg.hip_interframe.ang_vel_in(self.pelvis.frame)
        assert w.dot(self.pelvis.y) == self.hip.u


class TestSphericalHipTorque:
    @pytest.mark.parametrize("load_group_cls", [
        SphericalHipTorque])
    def test_invalid_type(self, load_group_cls) -> None:
        with pytest.raises(TypeError):
            TestPinLeftHipJoint("hip").add_load_groups(load_group_cls("hip"))

    @pytest.mark.parametrize("load_group_cls", [
        SphericalHipTorque])
    def test_descriptions(self, load_group_cls) -> None:
        _test_descriptions(load_group_cls("hip"))

    @staticmethod
    def _get_test_torques_info(hip_cls: type, leg_cls: type, load_group_cls: type
                               ) -> tuple:
        model = HipModel("model")
        model.hip = hip_cls("hip")
        model.pelvis = PlanarPelvis("pelvis")
        model.leg = leg_cls("leg")
        load_group = load_group_cls("hip")
        model.hip.add_load_groups(load_group)
        model.define_all()
        assert len(load_group.system.loads) == 2
        w = model.leg.hip_interframe.ang_vel_in(model.pelvis.frame)
        flex_axis = w.xreplace({model.hip.u[1]: 0, model.hip.u[2]: 0}).normalize()
        add_axis = w.xreplace({model.hip.u[0]: 0, model.hip.u[2]: 0}).normalize()
        rot_axis = w.xreplace({model.hip.u[0]: 0, model.hip.u[1]: 0}).normalize()
        return model, load_group, flex_axis, add_axis, rot_axis

    @pytest.mark.parametrize("hip_cls, leg_cls", [
        (SphericalLeftHip, TwoPinStickLeftLeg),
        (SphericalRightHip, TwoPinStickRightLeg)])
    def test_torque_loads(self, hip_cls, leg_cls) -> None:
        model, load_group, flex_axis, add_axis, rot_axis = self._get_test_torques_info(
            hip_cls, leg_cls, SphericalHipTorque)
        t_flex, t_add, t_rot = (load_group.symbols[name] for name in (
            "T_flexion", "T_adduction", "T_rotation"))
        for load in load_group.system.loads:
            if load.frame == model.leg.thigh.frame:
                assert check_zero(
                    load.torque.xreplace({t_add: 0, t_rot: 0}).dot(flex_axis) - t_flex)
                assert check_zero(
                    load.torque.xreplace({t_flex: 0, t_rot: 0}).dot(add_axis) - t_add)
                assert check_zero(
                    load.torque.xreplace({t_flex: 0, t_add: 0}).dot(rot_axis) - t_rot)
            else:
                assert load.frame == model.pelvis.frame
                assert check_zero(
                    load.torque.xreplace({t_add: 0, t_rot: 0}).dot(flex_axis) - -t_flex)
                assert check_zero(
                    load.torque.xreplace({t_flex: 0, t_rot: 0}).dot(add_axis) - -t_add)
                assert check_zero(
                    load.torque.xreplace({t_flex: 0, t_add: 0}).dot(rot_axis) - -t_rot)
