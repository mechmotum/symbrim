from __future__ import annotations

import pytest
from brim.rider.arms import (
    LeftArmBase,
    PinElbowStickLeftArm,
    PinElbowStickRightArm,
    RightArmBase,
)
from brim.utilities.testing import _test_descriptions
from sympy import simplify, zeros
from sympy.physics.mechanics import Point, ReferenceFrame, RigidBody


@pytest.mark.parametrize("arm_cls, base_cls", [
    (PinElbowStickLeftArm, LeftArmBase),
    (PinElbowStickRightArm, RightArmBase)])
class TestArmBase:
    def test_types(self, arm_cls, base_cls) -> None:
        arm = arm_cls("arm")
        arm.define_objects()
        assert isinstance(arm, base_cls)
        assert isinstance(arm.shoulder, RigidBody)
        assert isinstance(arm.hand, RigidBody)
        assert isinstance(arm.shoulder_interpoint, Point)
        assert isinstance(arm.hand_interpoint, Point)
        assert isinstance(arm.shoulder_interframe, ReferenceFrame)
        assert isinstance(arm.hand_interframe, ReferenceFrame)

    def test_descriptions(self, arm_cls, base_cls) -> None:
        arm = arm_cls("arm")
        _test_descriptions(arm)


@pytest.mark.parametrize("arm_cls", [PinElbowStickLeftArm, PinElbowStickRightArm])
class TestPinElbowStickArm:
    @pytest.fixture(autouse=True)
    def _setup(self, arm_cls: type) -> None:
        self.arm = arm_cls("arm")
        self.arm.define_objects()
        self.arm.define_kinematics()
        self.arm.define_loads()
        self.arm.define_constraints()
        self.l_u, self.l_f, self.l_uc, self.l_fc = (self.arm.symbols[name] for name in (
            "l_upper_arm", "l_forearm", "l_upper_arm_com", "l_forearm_com"))

    def test_kinematics(self) -> None:
        r = self.arm.hand_interpoint.pos_from(self.arm.shoulder_interpoint)
        r_val = self.l_u * self.arm.upper_arm.z + self.l_f * self.arm.forearm.z
        assert simplify((r - r_val).to_matrix(self.arm.upper_arm.frame)) == zeros(3, 1)
        assert self.arm.upper_arm.masscenter.pos_from(
            self.arm.shoulder_interpoint) == self.l_uc * self.arm.upper_arm.z
        assert self.arm.forearm.masscenter.pos_from(
            self.arm.system.joints[0].child_point) == self.l_fc * self.arm.forearm.z
        assert self.arm.forearm.frame.ang_vel_in(self.arm.upper_arm.frame).dot(
            self.arm.upper_arm.y) == self.arm.u
