from __future__ import annotations

import pytest
from brim.bicycle.front_frames import RigidFrontFrameMoore
from brim.brim.base_connections import HandGripsBase
from brim.brim.handgrips import HolonomicHandGrips, SpringDamperHandGrips
from brim.rider.arms import PinElbowStickLeftArm, PinElbowStickRightArm
from brim.utilities.testing import _test_descriptions, create_model_of_connection
from sympy import Symbol
from sympy.physics.mechanics import Vector, dynamicsymbols


@pytest.mark.parametrize("hand_grip_cls", [HolonomicHandGrips, SpringDamperHandGrips])
class TestSteerConnectionBase:
    @pytest.fixture()
    def _setup(self, hand_grip_cls) -> None:
        self.model = create_model_of_connection(hand_grip_cls)("model")
        self.model.front_frame = RigidFrontFrameMoore("front_frame")
        self.model.left_arm = PinElbowStickLeftArm("left_arm")
        self.model.right_arm = PinElbowStickRightArm("right_arm")
        self.model.conn = hand_grip_cls("steer_connection")
        self.model.define_connections()
        self.model.define_objects()
        # Define kinematics with enough degrees of freedom
        self.q = dynamicsymbols("q1:5")
        self.model.left_arm.hand_interframe.orient_axis(
            self.model.front_frame.frame, self.model.front_frame.steer_axis, self.q[0])
        self.model.left_arm.shoulder_interpoint.set_pos(
            self.model.front_frame.left_handgrip,
            self.q[1] * self.model.front_frame.steer_axis)
        self.model.right_arm.hand_interframe.orient_axis(
            self.model.front_frame.frame, self.model.front_frame.steer_axis, self.q[2])
        self.model.right_arm.shoulder_interpoint.set_pos(
            self.model.front_frame.right_handgrip,
            self.q[3] * self.model.front_frame.steer_axis)
        self.model.define_kinematics()
        self.model.define_loads()
        self.model.define_constraints()

    def test_types(self, _setup) -> None:
        assert isinstance(self.model.conn, HandGripsBase)

    def test_descriptions(self, _setup) -> None:
        _test_descriptions(self.model.conn)

    @pytest.mark.parametrize("side, arm_cls", [
        ("left", PinElbowStickLeftArm), ("right", PinElbowStickRightArm)])
    def test_single_arm(self, hand_grip_cls, side, arm_cls) -> None:
        self.model = create_model_of_connection(hand_grip_cls)("model")
        self.model.front_frame = RigidFrontFrameMoore("front_frame")
        setattr(self.model, side + "_arm", arm_cls(side + "_arm"))
        self.model.conn = hand_grip_cls("steer_connection")
        self.model.define_connections()
        self.model.define_objects()
        # Define kinematics with enough degrees of freedom
        self.q = dynamicsymbols("q1:3")
        getattr(self.model, side + "_arm").hand_interframe.orient_axis(
            self.model.front_frame.frame, self.model.front_frame.steer_axis, self.q[0])
        getattr(self.model, side + "_arm").shoulder_interpoint.set_pos(
            self.model.front_frame.left_handgrip,
            self.q[1] * self.model.front_frame.steer_axis)
        self.model.define_kinematics()
        self.model.define_loads()
        self.model.define_constraints()


class TestHolonomicHandGrip:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = create_model_of_connection(HolonomicHandGrips)("model")
        self.model.front_frame = RigidFrontFrameMoore("front_frame")
        self.model.left_arm = PinElbowStickLeftArm("left_arm")
        self.model.right_arm = PinElbowStickRightArm("right_arm")
        self.model.conn = HolonomicHandGrips("steer_connection")
        self.model.define_connections()
        self.model.define_objects()
        self.model.left_arm.hand_interframe.orient_axis(
            self.model.front_frame.frame, self.model.front_frame.steer_axis, 0)
        self.model.right_arm.hand_interframe.orient_axis(
            self.model.front_frame.frame, self.model.front_frame.steer_axis, 0)
        self.front_frame, self.left_arm, self.right_arm, self.conn = (
            self.model.front_frame, self.model.left_arm, self.model.right_arm,
            self.model.conn)

    def test_all_constraints(self) -> None:
        q = dynamicsymbols("q1:7")
        self.left_arm.hand_interpoint.set_pos(
            self.front_frame.left_handgrip,
            sum(qi * v for qi, v in zip(q[:3], self.front_frame.frame)))
        self.right_arm.hand_interpoint.set_pos(
            self.front_frame.right_handgrip,
            sum(qi * v for qi, v in zip(q[3:], self.front_frame.frame)))
        self.model.define_kinematics()
        self.model.define_loads()
        self.model.define_constraints()
        assert len(self.conn.system.holonomic_constraints) == 6
        expected_constraints = list(q)
        for constr in self.conn.system.holonomic_constraints:
            for exp_constr in expected_constraints:
                if constr.xreplace({exp_constr: 0}) == 0:
                    expected_constraints.remove(exp_constr)
        assert not expected_constraints

    def test_not_fully_constraint(self) -> None:
        q, d = dynamicsymbols("q"), Symbol("d")
        self.left_arm.hand_interpoint.set_pos(self.front_frame.left_handgrip, 0)
        self.right_arm.hand_interpoint.set_pos(
            self.front_frame.right_handgrip,
            q * self.front_frame.frame.x + 2 * d * self.front_frame.frame.x)
        self.model.define_kinematics()
        self.model.define_loads()
        self.model.define_constraints()
        assert len(self.conn.system.holonomic_constraints) == 1
        assert self.conn.system.holonomic_constraints[0].xreplace({q: 0.6, d: -0.3}
                                                                  ) == 0

    def test_constant_constraint(self) -> None:
        q, d = dynamicsymbols("q"), Symbol("d")
        self.left_arm.hand_interpoint.set_pos(self.front_frame.left_handgrip, 0)
        self.right_arm.hand_interpoint.set_pos(
            self.front_frame.right_handgrip,
            q * self.front_frame.frame.x + d * self.front_frame.frame.y)
        self.model.define_kinematics()
        self.model.define_loads()
        with pytest.raises(ValueError):
            self.model.define_constraints()


class TestSpringDamperHandGrip:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = create_model_of_connection(SpringDamperHandGrips)("model")
        self.model.front_frame = RigidFrontFrameMoore("front_frame")
        self.model.left_arm = PinElbowStickLeftArm("left_arm")
        self.model.right_arm = PinElbowStickRightArm("right_arm")
        self.model.conn = SpringDamperHandGrips("steer_connection")
        self.model.define_connections()
        self.model.define_objects()
        self.model.left_arm.hand_interframe.orient_axis(
            self.model.front_frame.frame, self.model.front_frame.steer_axis, 0)
        self.model.right_arm.hand_interframe.orient_axis(
            self.model.front_frame.frame, self.model.front_frame.steer_axis, 0)
        self.front_frame, self.left_arm, self.right_arm, self.conn = (
            self.model.front_frame, self.model.left_arm, self.model.right_arm,
            self.model.conn)

    def test_loads(self) -> None:
        q1, q2 = dynamicsymbols("q1:3")
        self.left_arm.hand_interpoint.set_pos(
            self.front_frame.left_handgrip, q1 * self.front_frame.frame.x)
        self.right_arm.hand_interpoint.set_pos(
            self.front_frame.right_handgrip, -q2 * self.front_frame.frame.y)
        self.model.define_kinematics()
        self.model.define_loads()
        self.model.define_constraints()
        loads_indi = [ld for act in self.conn.system.actuators for ld in act.to_loads()]
        locations, loads = {}, []
        for ld in loads_indi:
            if ld.location not in locations:
                locations[ld.location] = len(loads)
                loads.append(ld)
            else:
                loads[locations[ld.location]] = ld.__class__(
                    ld.location, ld.vector + loads[locations[ld.location]].vector)
        assert len(loads) == 4
        k, c = self.conn.symbols["k"], self.conn.symbols["c"]
        for ld in loads:
            if ld.location == self.front_frame.left_handgrip:
                assert (ld.vector - (k * q1 + c * q1.diff()) * self.front_frame.frame.x
                        ).simplify() == Vector(0)
            elif ld.location == self.left_arm.hand_interpoint:
                assert (ld.vector + (k * q1 + c * q1.diff()) * self.front_frame.frame.x
                        ).simplify() == Vector(0)
            elif ld.location == self.front_frame.right_handgrip:
                assert (ld.vector - (-k * q2 - c * q2.diff()) * self.front_frame.frame.y
                        ).simplify() == Vector(0)
            else:
                assert ld.location == self.right_arm.hand_interpoint
                assert (ld.vector + (-k * q2 - c * q2.diff()) * self.front_frame.frame.y
                        ).simplify() == Vector(0)
