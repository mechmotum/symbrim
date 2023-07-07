from __future__ import annotations

import pytest
from brim.core import ConnectionRequirement, ModelBase, ModelRequirement
from brim.rider.arms import ArmBase, PinElbowStickLeftArm, PinElbowStickRightArm
from brim.rider.base_connections import (
    LeftShoulderBase,
    RightShoulderBase,
    ShoulderBase,
)
from brim.rider.shoulder_joints import (
    SphericalLeftShoulder,
    SphericalRightShoulder,
    SphericalShoulderSpringDamper,
    SphericalShoulderTorque,
)
from brim.rider.torso import PlanarTorso, TorsoBase
from brim.utilities.testing import _test_descriptions
from brim.utilities.utilities import check_zero


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
        shoulder.torso = PlanarTorso("torso")
        shoulder.arm = arm_cls("arm")
        assert isinstance(shoulder, base_cls)

    def test_descriptions(self, shoulder_cls, arm_cls, base_cls) -> None:
        shoulder = shoulder_cls("shoulder")
        shoulder.torso = PlanarTorso("torso")
        shoulder.arm = arm_cls("arm")
        _test_descriptions(shoulder)


class TestSphericalLeftShoulderJoint:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = ShoulderModel("model")
        self.model.shoulder = SphericalLeftShoulder("shoulder")
        self.model.torso = PlanarTorso("torso")
        self.model.arm = PinElbowStickLeftArm("arm")
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


class TestSphericalRightShoulderJoint:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = ShoulderModel("model")
        self.model.shoulder = SphericalRightShoulder("shoulder")
        self.model.torso = PlanarTorso("torso")
        self.model.arm = PinElbowStickRightArm("arm")
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

class TestSphericalShoulderTorque:
    @pytest.mark.parametrize("load_group_cls", [
        SphericalShoulderTorque, SphericalShoulderSpringDamper])
    def test_invalid_type(self, load_group_cls) -> None:
        with pytest.raises(TypeError):
            PlanarTorso("torso").add_load_groups(load_group_cls("shoulder"))

    @pytest.mark.parametrize("load_group_cls", [
        SphericalShoulderTorque, SphericalShoulderSpringDamper])
    def test_descriptions(self, load_group_cls) -> None:
        _test_descriptions(load_group_cls("shoulder"))

    @staticmethod
    def _get_test_torques_info(shoulder_cls: type, arm_cls: type, load_group_cls: type
                               ) -> tuple:
        model = ShoulderModel("model")
        model.shoulder = shoulder_cls("shoulder")
        model.torso = PlanarTorso("torso")
        model.arm = arm_cls("arm")
        load_group = load_group_cls("shoulder")
        model.shoulder.add_load_groups(load_group)
        model.define_all()
        assert len(load_group.system.loads) == 2
        w = model.arm.shoulder_interframe.ang_vel_in(model.torso.frame)
        flex_axis = w.xreplace(
            {model.shoulder.u[1]: 0, model.shoulder.u[2]: 0}).normalize()
        abd_axis = w.xreplace(
            {model.shoulder.u[0]: 0, model.shoulder.u[2]: 0}).normalize()
        rot_axis = w.xreplace(
            {model.shoulder.u[0]: 0, model.shoulder.u[1]: 0}).normalize()
        return model, load_group, flex_axis, abd_axis, rot_axis

    @pytest.mark.parametrize("shoulder_cls, leg_cls", [
        (SphericalLeftShoulder, PinElbowStickLeftArm),
        (SphericalRightShoulder, PinElbowStickRightArm)])
    def test_torque_loads(self, shoulder_cls, leg_cls) -> None:
        model, load_group, flex_axis, abd_axis, rot_axis = self._get_test_torques_info(
            shoulder_cls, leg_cls, SphericalShoulderTorque)
        t_flex, t_add, t_rot = (load_group.symbols[name] for name in (
            "T_flexion", "T_abduction", "T_rotation"))
        for load in load_group.system.loads:
            if load.frame == model.arm.shoulder_interframe:
                assert check_zero(
                    load.torque.xreplace({t_add: 0, t_rot: 0}).dot(flex_axis) - t_flex)
                assert check_zero(
                    load.torque.xreplace({t_flex: 0, t_rot: 0}).dot(abd_axis) - t_add)
                assert check_zero(
                    load.torque.xreplace({t_flex: 0, t_add: 0}).dot(rot_axis) - t_rot)
            else:
                assert load.frame == model.torso.frame
                assert check_zero(
                    load.torque.xreplace({t_add: 0, t_rot: 0}).dot(flex_axis) - -t_flex)
                assert check_zero(
                    load.torque.xreplace({t_flex: 0, t_rot: 0}).dot(abd_axis) - -t_add)
                assert check_zero(
                    load.torque.xreplace({t_flex: 0, t_add: 0}).dot(rot_axis) - -t_rot)

    @pytest.mark.parametrize("shoulder_cls, leg_cls", [
        (SphericalLeftShoulder, PinElbowStickLeftArm),
        (SphericalRightShoulder, PinElbowStickRightArm)])
    def test_spring_damper_loads(self, shoulder_cls, leg_cls) -> None:
        model, load_group, flex_axis, abd_axis, rot_axis = self._get_test_torques_info(
            shoulder_cls, leg_cls, SphericalShoulderSpringDamper)
        syms = [tuple(load_group.symbols[f"{tp}_{name}"] for tp in ("k", "c", "q_ref"))
                for name in ("flexion", "abduction", "rotation")]
        zero = [{sym: 0 for sym in syms_tp} for syms_tp in syms]

        def torque(syms, q, u):
            return -syms[0] * (q - syms[2]) - syms[1] * u

        for load in load_group.system.loads:
            if load.frame == model.arm.shoulder_interframe:
                assert check_zero(
                    load.torque.xreplace({**zero[1], **zero[2]}).dot(flex_axis) -
                    torque(syms[0], model.shoulder.q[0], model.shoulder.u[0]))
                assert check_zero(
                    load.torque.xreplace({**zero[0], **zero[2]}).dot(abd_axis) -
                    torque(syms[1], model.shoulder.q[1], model.shoulder.u[1]))
                assert check_zero(
                    load.torque.xreplace({**zero[0], **zero[1]}).dot(rot_axis) -
                    torque(syms[2], model.shoulder.q[2], model.shoulder.u[2]))
            else:
                assert load.frame == model.torso.frame
                assert check_zero(
                    load.torque.xreplace({**zero[1], **zero[2]}).dot(flex_axis) +
                    torque(syms[0], model.shoulder.q[0], model.shoulder.u[0]))
                assert check_zero(
                    load.torque.xreplace({**zero[0], **zero[2]}).dot(abd_axis) +
                    torque(syms[1], model.shoulder.q[1], model.shoulder.u[1]))
                assert check_zero(
                    load.torque.xreplace({**zero[0], **zero[1]}).dot(rot_axis) +
                    torque(syms[2], model.shoulder.q[2], model.shoulder.u[2]))
