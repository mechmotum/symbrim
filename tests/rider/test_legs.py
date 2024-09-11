from __future__ import annotations

import pytest
from sympy import simplify, zeros
from sympy.physics.mechanics import Point, ReferenceFrame, RigidBody

from brim.rider.arms import PinElbowStickLeftArm
from brim.rider.legs import (
    LeftLegBase,
    RightLegBase,
    TwoPinLegSpringDamper,
    TwoPinLegTorque,
    TwoPinStickLeftLeg,
    TwoPinStickRightLeg,
)
from brim.utilities.testing import _test_descriptions
from brim.utilities.utilities import check_zero

try:
    from brim.utilities.plotting import PlotModel
except ImportError:
    PlotModel = None

@pytest.mark.parametrize("leg_cls, base", [
    (TwoPinStickLeftLeg, LeftLegBase),
    (TwoPinStickRightLeg, RightLegBase)])
class TestLegBase:
    def test_types(self, leg_cls, base) -> None:
        leg = leg_cls("leg")
        leg.define_objects()
        assert isinstance(leg, base)
        assert isinstance(leg.hip, RigidBody)
        assert isinstance(leg.foot, RigidBody)
        assert isinstance(leg.hip_interpoint, Point)
        assert isinstance(leg.foot_interpoint, Point)
        assert isinstance(leg.hip_interframe, ReferenceFrame)
        assert isinstance(leg.foot_interframe, ReferenceFrame)

    def test_descriptions(self, leg_cls, base) -> None:
        _test_descriptions(leg_cls("leg"))

    @pytest.mark.skipif(PlotModel is None, reason="symmeplot not installed")
    def test_plotting(self, leg_cls, base):
        leg = leg_cls("leg")
        leg.define_all()
        plot_model = PlotModel(leg.system.frame, leg.system.fixed_point, leg)
        assert plot_model.children


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
            -self.leg.thigh.y) == sum(self.leg.u)


class TestTwoPinLegTorque:
    def test_invalid_type(self) -> None:
        with pytest.raises(TypeError):
            PinElbowStickLeftArm("arm").add_load_groups(TwoPinLegTorque("leg"))

    def test_descriptions(self) -> None:
        _test_descriptions(TwoPinLegTorque("leg"))

    @pytest.mark.parametrize("leg_cls", [TwoPinStickLeftLeg, TwoPinStickRightLeg])
    def test_loads(self, leg_cls) -> None:
        leg = leg_cls("leg")
        load_group = TwoPinLegTorque("torque")
        leg.add_load_groups(load_group)
        leg.define_all()
        system = leg.to_system()
        assert len(system.actuators) == 2
        rot_axis = leg.shank.y
        for actuator in system.actuators:
            loads = actuator.to_loads()
            if actuator.target_frame == leg.shank.frame:
                torque = load_group.symbols["T_knee"]
                for load in loads:
                    if load.frame == leg.shank.frame:
                        assert check_zero(load.torque.dot(rot_axis) - torque)
                    else:
                        assert load.frame == leg.thigh.frame
                        assert check_zero(load.torque.dot(rot_axis) - -torque)
            else:
                torque = load_group.symbols["T_ankle"]
                for load in loads:
                    if load.frame == leg.foot.frame:
                        assert check_zero(load.torque.dot(rot_axis) - torque)
                    else:
                        assert load.frame == leg.shank.frame
                        assert check_zero(load.torque.dot(rot_axis) - -torque)


class TestPinElbowSpringDamper:
    def test_invalid_type(self) -> None:
        with pytest.raises(TypeError):
            PinElbowStickLeftArm("arm").add_load_groups(TwoPinLegSpringDamper("leg"))

    def test_descriptions(self) -> None:
        _test_descriptions(TwoPinLegSpringDamper("leg"))

    @pytest.mark.parametrize("leg_cls", [TwoPinStickLeftLeg, TwoPinStickRightLeg])
    def test_loads(self, leg_cls) -> None:
        leg = leg_cls("leg")
        load_group = TwoPinLegSpringDamper("spring_damper")
        leg.add_load_groups(load_group)
        leg.define_all()
        system = leg.to_system()
        assert len(system.actuators) == 2
        rot_axis = leg.shank.y
        for actuator in system.actuators:
            loads = actuator.to_loads()
            if actuator.target_frame == leg.shank.frame:
                k, c, q_ref = (
                    load_group.symbols[name + "_knee"] for name in ("k", "c", "q_ref"))
                torque = (k * (q_ref - leg.q[0]) - c * leg.u[0])
                for load in loads:
                    if load.frame == leg.shank.frame:
                        assert check_zero(load.torque.dot(rot_axis) - torque)
                    else:
                        assert load.frame == leg.thigh.frame
                        assert check_zero(load.torque.dot(rot_axis) - -torque)
            else:
                k, c, q_ref = (
                    load_group.symbols[name + "_ankle"] for name in ("k", "c", "q_ref"))
                torque = (k * (q_ref - leg.q[1]) - c * leg.u[1])
                for load in loads:
                    if load.frame == leg.foot.frame:
                        assert check_zero(load.torque.dot(rot_axis) - torque)
                    else:
                        assert load.frame == leg.shank.frame
                        assert check_zero(load.torque.dot(rot_axis) - -torque)
