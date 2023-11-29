import pytest
from brim.bicycle.front_frames import (
    RigidFrontFrame,
    RigidFrontFrameMoore,
    SuspensionRigidFrontFrame,
    SuspensionRigidFrontFrameMoore,
)
from brim.core import Attachment, Hub
from brim.utilities.testing import _test_descriptions
from sympy.physics.mechanics import Point, System, Vector

try:
    from brim.utilities.plotting import PlotModel
    from symmeplot import PlotBody, PlotLine
except ImportError:
    PlotModel = None


class TestFrontFrame:
    @pytest.mark.parametrize("base_cls, expected_cls", [
        (RigidFrontFrame, RigidFrontFrameMoore),
        (SuspensionRigidFrontFrame, SuspensionRigidFrontFrameMoore),
    ])
    def test_default(self, base_cls, expected_cls) -> None:
        front = base_cls("front")
        assert front.name == "front"
        assert isinstance(front, expected_cls)

    @pytest.mark.parametrize("convention_name, base_cls, expected_cls", [
        ("moore", RigidFrontFrame, RigidFrontFrameMoore),
        ("moore", SuspensionRigidFrontFrame, SuspensionRigidFrontFrameMoore),
    ])
    def test_init(self, convention_name, base_cls, expected_cls) -> None:
        front = base_cls.from_convention(convention_name, "front")
        assert isinstance(front, expected_cls)

    @pytest.mark.parametrize("base_cls", [RigidFrontFrame, SuspensionRigidFrontFrame])
    def test_init_error(self, base_cls) -> None:
        with pytest.raises(ValueError):
            base_cls.from_convention("not_implemented", "front")

    @pytest.mark.parametrize("frame_cls", [
        RigidFrontFrameMoore, SuspensionRigidFrontFrameMoore])
    def test_descriptions(self, frame_cls) -> None:
        _test_descriptions(frame_cls("front"))

    @pytest.mark.parametrize("cls", [
        RigidFrontFrameMoore, SuspensionRigidFrontFrameMoore])
    def test_define_all(self, cls) -> None:
        front = cls("front")
        front.define_all()
        assert isinstance(front.system, System)
        assert len(front.system.bodies) >= 1
        assert isinstance(front.steer_hub, Hub)
        assert isinstance(front.wheel_hub, Hub)
        assert isinstance(front.left_hand_grip, Attachment)
        assert isinstance(front.right_hand_grip, Attachment)
        for body in front.system.bodies:
            body.masscenter.pos_from(front.system.origin)
        for attachment in (front.steer_hub, front.wheel_hub, front.left_hand_grip,
                           front.right_hand_grip):
            attachment.frame.dcm(front.system.frame)
            attachment.point.pos_from(front.system.origin)

    @pytest.mark.skipif(PlotModel is None, reason="symmeplot not installed")
    @pytest.mark.parametrize("cls, n_children", [
        (RigidFrontFrameMoore, 2), (SuspensionRigidFrontFrameMoore, 2)])
    def test_plotting(self, cls, n_children):
        front = cls("front")
        front.define_all()
        plot_model = PlotModel(front.system.frame, front.system.origin, front)
        assert len(plot_model.children) == n_children
        assert any(isinstance(obj, PlotBody) for obj in plot_model.children)
        assert any(isinstance(obj, PlotLine) for obj in plot_model.children)


class TestRigidFrontFrameMoore:
    def test_default(self) -> None:
        front = RigidFrontFrameMoore("front")
        front.define_objects()
        assert front.wheel_hub.axis == front.body.y

    def test_kinematics(self) -> None:
        front = RigidFrontFrameMoore("front")
        front.define_objects()
        front.define_kinematics()
        # Test velocities
        assert front.body.masscenter.vel(front.body.frame) == 0
        assert front.steer_hub.point.vel(front.body.frame) == 0
        assert front.wheel_hub.point.vel(front.body.frame) == 0
        assert front.left_hand_grip.point.vel(front.body.frame) == 0
        assert front.right_hand_grip.point.vel(front.body.frame) == 0


class TestSuspensionRigidFrontFrameMoore:
    def test_default(self) -> None:
        front = SuspensionRigidFrontFrameMoore("front")
        front.define_objects()
        front.define_kinematics()
        assert isinstance(front.suspension_stanchions, Point)
        assert isinstance(front.suspension_lowers, Point)
        assert front.wheel_hub.axis == front.body.y

    def test_kinematics(self) -> None:
        front = SuspensionRigidFrontFrameMoore("front")
        front.define_objects()
        front.define_kinematics()
        # Test velocities
        assert front.body.masscenter.vel(front.body.frame) == 0
        assert front.steer_hub.point.vel(front.body.frame) == 0
        assert front.suspension_stanchions.vel(front.body.frame) == 0
        assert front.wheel_hub.point.vel(front.body.frame) == -front.u[0] * front.body.z
        assert (front.suspension_lowers.vel(front.body.frame) ==
                -front.u[0] * front.body.z)
        assert front.left_hand_grip.point.vel(front.body.frame) == 0
        assert front.right_hand_grip.point.vel(front.body.frame) == 0
        assert front.wheel_hub.frame.ang_vel_in(front.steer_hub.frame) == Vector(0)

    def test_loads(self) -> None:
        front = SuspensionRigidFrontFrameMoore("front")
        front.define_all()
        loads = list(front.system.loads) + [
            act.to_loads() for act in front.system.actuators]
        assert len(loads) == 2
        if loads[0][0] == front.suspension_stanchions:
            assert loads[1][0] == front.suspension_lowers
            stanchion_force, slider_force = loads[0][1], loads[1][1]
        else:
            assert loads[0][0] == front.suspension_lowers
            assert loads[1][0] == front.suspension_stanchions
            stanchion_force, slider_force = loads[1][1], loads[0][1]
        q, u, k, c = front.q[0], front.u[0], front.symbols["k"], front.symbols["c"]
        stanchion_force = stanchion_force.xreplace({k: 1000, c: 50})
        slider_force = slider_force.xreplace({k: 1000, c: 50})
        steer_axis_up = -front.steer_hub.axis
        assert stanchion_force.dot(steer_axis_up).xreplace({q: 0.02, u: -0.1}) == 15.
        assert slider_force.dot(steer_axis_up).xreplace({q: 0.02, u: -0.1}) == -15.
        assert stanchion_force.dot(steer_axis_up).xreplace({q: 0.02, u: 0.1}) == 25.
        assert slider_force.dot(steer_axis_up).xreplace({q: 0.02, u: 0.1}) == -25.
