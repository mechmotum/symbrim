from __future__ import annotations

import pytest
from brim.rider.arms import (
    LeftArmBase,
    PinElbowSpringDamper,
    PinElbowStickLeftArm,
    PinElbowStickRightArm,
    PinElbowTorque,
    RightArmBase,
)
from brim.rider.legs import TwoPinStickLeftLeg
from brim.utilities.testing import _test_descriptions
from brim.utilities.utilities import check_zero
from sympy import simplify, zeros
from sympy.physics.mechanics import Point, ReferenceFrame, RigidBody

try:
    from brim.utilities.plotting import PlotModel
except ImportError:
    PlotModel = None


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
        _test_descriptions(arm_cls("arm"))

    @pytest.mark.skipif(PlotModel is None, reason="symmeplot not installed")
    def test_plotting(self, arm_cls, base_cls):
        arm = arm_cls("arm")
        arm.define_all()
        plot_model = PlotModel(arm.system.frame, arm.system.fixed_point, arm)
        assert plot_model.children


@pytest.mark.parametrize("arm_cls", [PinElbowStickLeftArm, PinElbowStickRightArm])
class TestPinElbowStickArm:
    @pytest.fixture(autouse=True)
    def _setup(self, arm_cls: type) -> None:
        self.arm = arm_cls("arm")
        self.arm.define_all()
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
            self.arm.upper_arm.y) == self.arm.u[0]


class TestPinElbowTorque:
    def test_invalid_type(self) -> None:
        with pytest.raises(TypeError):
            TwoPinStickLeftLeg("leg").add_load_groups(PinElbowTorque("arm"))

    def test_descriptions(self) -> None:
        _test_descriptions(PinElbowTorque("arm"))

    @pytest.mark.parametrize("arm_cls", [PinElbowStickLeftArm, PinElbowStickRightArm])
    def test_loads(self, arm_cls) -> None:
        arm = arm_cls("arm")
        elbow_load = PinElbowTorque("elbow_torque")
        arm.add_load_groups(elbow_load)
        arm.define_all()
        system = arm.to_system()
        assert len(system.actuators) == 1
        torque = elbow_load.symbols["T"]
        loads = system.actuators[0].to_loads()
        # Carefully check the signs of the torques.
        rot_axis = arm.forearm.frame.ang_vel_in(arm.upper_arm.frame).normalize()
        for load in loads:
            if load.frame == arm.forearm.frame:
                assert check_zero(load.torque.dot(rot_axis) - torque)
            else:
                assert load.frame == arm.upper_arm.frame
                assert check_zero(load.torque.dot(rot_axis) - -torque)


class TestPinElbowSpringDamper:
    def test_invalid_type(self) -> None:
        with pytest.raises(TypeError):
            TwoPinStickLeftLeg("leg").add_load_groups(PinElbowSpringDamper("arm"))

    def test_descriptions(self) -> None:
        _test_descriptions(PinElbowSpringDamper("arm"))

    @pytest.mark.parametrize("arm_cls", [PinElbowStickLeftArm, PinElbowStickRightArm])
    def test_loads(self, arm_cls) -> None:
        arm = arm_cls("arm")
        elbow_load = PinElbowSpringDamper("elbow_spring_damper")
        arm.add_load_groups(elbow_load)
        arm.define_all()
        system = arm.to_system()
        assert len(system.actuators) == 1
        k, c, q_ref = (elbow_load.symbols[name] for name in ("k", "c", "q_ref"))
        loads = system.actuators[0].to_loads()
        # Carefully check the signs of the torques.
        rot_axis = arm.forearm.frame.ang_vel_in(arm.upper_arm.frame).normalize()
        for load in loads:
            if load.frame == arm.forearm.frame:
                assert check_zero(load.torque.dot(rot_axis) -
                                  (k * (q_ref - arm.q[0]) - c * arm.u[0]))
            else:
                assert load.frame == arm.upper_arm.frame
                assert check_zero(load.torque.dot(rot_axis) -
                                  (-k * (q_ref - arm.q[0]) + c * arm.u[0]))
