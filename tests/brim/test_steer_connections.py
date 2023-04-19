from __future__ import annotations

import pytest
from brim.bicycle.front_frames import RigidFrontFrameMoore
from brim.brim.base_connections import SteerConnectionBase
from brim.brim.steer_connections import HolonomicSteerConnection
from brim.rider.arms import PinElbowStickLeftArm, PinElbowStickRightArm
from brim.utilities.testing import _test_descriptions, create_model_of_connection
from sympy import Symbol
from sympy.physics.mechanics import dynamicsymbols


@pytest.mark.parametrize("steer_cls", [HolonomicSteerConnection])
class TestSteerConnectionBase:
    @pytest.fixture(autouse=True)
    def _setup(self, steer_cls) -> None:
        self.model = create_model_of_connection(steer_cls)("model")
        self.model.steer = RigidFrontFrameMoore("front_frame")
        self.model.left_arm = PinElbowStickLeftArm("left_arm")
        self.model.right_arm = PinElbowStickRightArm("right_arm")
        self.model.conn = steer_cls("steer_connection")
        self.model.define_connections()
        self.model.define_objects()
        # Define kinematics with enough degrees of freedom
        self.q = dynamicsymbols("q1:5")
        self.model.left_arm.hand_interframe.orient_axis(
            self.model.steer.frame, self.model.steer.steer_axis, self.q[0])
        self.model.left_arm.shoulder_interpoint.set_pos(
            self.model.steer.left_handgrip, self.q[1] * self.model.steer.steer_axis)
        self.model.right_arm.hand_interframe.orient_axis(
            self.model.steer.frame, self.model.steer.steer_axis, self.q[2])
        self.model.right_arm.shoulder_interpoint.set_pos(
            self.model.steer.right_handgrip, self.q[3] * self.model.steer.steer_axis)
        self.model.define_kinematics()
        self.model.define_loads()
        self.model.define_constraints()

    def test_types(self) -> None:
        assert isinstance(self.model.conn, SteerConnectionBase)

    def test_descriptions(self) -> None:
        _test_descriptions(self.model.conn)


class TestHolonomicSteerConnection:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = create_model_of_connection(HolonomicSteerConnection)("model")
        self.model.steer = RigidFrontFrameMoore("front_frame")
        self.model.left_arm = PinElbowStickLeftArm("left_arm")
        self.model.right_arm = PinElbowStickRightArm("right_arm")
        self.model.conn = HolonomicSteerConnection("steer_connection")
        self.model.define_connections()
        self.model.define_objects()
        self.model.left_arm.hand_interframe.orient_axis(
            self.model.steer.frame, self.model.steer.steer_axis, 0)
        self.model.right_arm.hand_interframe.orient_axis(
            self.model.steer.frame, self.model.steer.steer_axis, 0)
        self.steer, self.left_arm, self.right_arm, self.conn = (
            self.model.steer, self.model.left_arm, self.model.right_arm,
            self.model.conn)

    def test_all_constraints(self) -> None:
        q = dynamicsymbols("q1:7")
        self.left_arm.hand_interpoint.set_pos(
            self.steer.left_handgrip,
            sum(qi * v for qi, v in zip(q[:3], self.steer.frame)))
        self.right_arm.hand_interpoint.set_pos(
            self.steer.right_handgrip,
            sum(qi * v for qi, v in zip(q[3:], self.steer.frame)))
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
        self.left_arm.hand_interpoint.set_pos(self.steer.left_handgrip, 0)
        self.right_arm.hand_interpoint.set_pos(
            self.steer.right_handgrip,
            q * self.steer.frame.x + 2 * d * self.steer.frame.x)
        self.model.define_kinematics()
        self.model.define_loads()
        self.model.define_constraints()
        assert len(self.conn.system.holonomic_constraints) == 1
        assert self.conn.system.holonomic_constraints[0].xreplace({q: 0.6, d: -0.3}
                                                                  ) == 0

    def test_constant_constraint(self) -> None:
        q, d = dynamicsymbols("q"), Symbol("d")
        self.left_arm.hand_interpoint.set_pos(self.steer.left_handgrip, 0)
        self.right_arm.hand_interpoint.set_pos(
            self.steer.right_handgrip,
            q * self.steer.frame.x + d * self.steer.frame.y)
        self.model.define_kinematics()
        self.model.define_loads()
        with pytest.raises(ValueError):
            self.model.define_constraints()
