from __future__ import annotations

import pytest
from brim.rider.legs import (
    LeftLegBase,
    RightLegBase,
    TwoPinStickLeftLeg,
    TwoPinStickRightLeg,
)
from sympy import simplify, zeros
from sympy.physics.mechanics import Point, ReferenceFrame, RigidBody


@pytest.mark.parametrize("leg_cls, base", [
    (TwoPinStickLeftLeg, LeftLegBase),
    (TwoPinStickRightLeg, RightLegBase)])
class TestLegBase:
    def test_types(self, leg_cls, base) -> None:
        arm = leg_cls("arm")
        arm.define_objects()
        assert isinstance(arm, base)
        assert isinstance(arm.hip, RigidBody)
        assert isinstance(arm.foot, RigidBody)
        assert isinstance(arm.hip_interpoint, Point)
        assert isinstance(arm.foot_interpoint, Point)
        assert isinstance(arm.hip_interframe, ReferenceFrame)
        assert isinstance(arm.foot_interframe, ReferenceFrame)

    def test_descriptions(self, leg_cls, base) -> None:
        arm = leg_cls("arm")
        arm.define_objects()
        for sym in arm.symbols.values():
            assert sym in arm.descriptions


@pytest.mark.parametrize("leg_cls", [TwoPinStickLeftLeg, TwoPinStickRightLeg])
class TestTwoPinStickLeg:
    @pytest.fixture(autouse=True)
    def _setup(self, leg_cls) -> None:
        self.leg = leg_cls("leg")
        self.leg.define_objects()
        self.leg.define_kinematics()
        self.leg.define_loads()
        self.leg.define_constraints()
        self.l_f, self.l_t, self.l_s, self.l_f_com, self.l_t_com, self.l_s_com = (
            self.leg.symbols[length] for length in (
            "l_foot", "l_thigh", "l_shank", "l_foot_com", "l_thigh_com", "l_shank_com"))

    def test_kinematics(self) -> None:
        r = self.leg.foot_interpoint.pos_from(self.leg.hip_interpoint)
        r_val = (self.l_f * self.leg.foot.x + self.l_s * self.leg.shank.z
                 + self.l_t * self.leg.thigh.z)
        assert simplify((r - r_val).to_matrix(self.leg.hip.frame)) == zeros(3, 1)
        assert self.leg.foot.masscenter.pos_from(
            self.leg.system.get_joint("leg_ankle").child_point
        ) == self.l_f_com * self.leg.foot.x
        assert self.leg.shank.masscenter.pos_from(
            self.leg.system.get_joint("leg_knee").child_point
        ) == self.l_s_com * self.leg.shank.z
        assert self.leg.thigh.masscenter.pos_from(
            self.leg.hip_interpoint) == self.l_t_com * self.leg.thigh.z
        assert self.leg.foot.frame.ang_vel_in(self.leg.hip.frame).dot(
            self.leg.thigh.y) == sum(self.leg.u)
