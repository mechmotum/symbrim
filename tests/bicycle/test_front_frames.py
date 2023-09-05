import pytest
from brim.bicycle.front_frames import (
    RigidFrontFrame,
    RigidFrontFrameMoore,
    SuspensionRigidFrontFrame,
    SuspensionRigidFrontFrameMoore,
)
from brim.utilities.testing import _test_descriptions
from sympy.physics.mechanics import Point

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


class TestRigidFrontFrameMoore:
    def test_default(self) -> None:
        front = RigidFrontFrameMoore("front")
        front.define_objects()
        assert front.name == "front"
        assert front.frame == front.body.frame
        assert isinstance(front.steer_attachment, Point)
        assert isinstance(front.wheel_attachment, Point)
        assert front.wheel_axis == front.y

    def test_kinematics(self) -> None:
        front = RigidFrontFrameMoore("front")
        front.define_objects()
        front.define_kinematics()
        # Test if kinematics is defined
        front.steer_attachment.pos_from(front.body.masscenter)
        front.wheel_attachment.pos_from(front.body.masscenter)
        front.left_hand_grip.pos_from(front.body.masscenter)
        front.right_hand_grip.pos_from(front.body.masscenter)
        # Test velocities
        assert front.body.masscenter.vel(front.frame) == 0
        assert front.steer_attachment.vel(front.frame) == 0
        assert front.wheel_attachment.vel(front.frame) == 0
        assert front.left_hand_grip.vel(front.frame) == 0
        assert front.right_hand_grip.vel(front.frame) == 0

    @pytest.mark.skipif(PlotModel is None, reason="symmeplot not installed")
    def test_plotting(self):
        front = RigidFrontFrameMoore("front")
        front.define_all()
        plot_model = PlotModel(front.system.frame, front.system.origin, front)
        assert len(plot_model.children) == 2
        assert any(isinstance(obj, PlotBody) for obj in plot_model.children)
        assert any(isinstance(obj, PlotLine) for obj in plot_model.children)


class TestSuspensionRigidFrontFrameMoore:
    def test_default(self) -> None:
        front = SuspensionRigidFrontFrameMoore("front")
        front.define_objects()
        assert front.name == "front"
        assert front.frame == front.body.frame
        assert isinstance(front.steer_attachment, Point)
        assert isinstance(front.wheel_attachment, Point)
        assert isinstance(front.left_hand_grip, Point)
        assert isinstance(front.right_hand_grip, Point)
        assert isinstance(front.suspension_stanchions, Point)
        assert isinstance(front.suspension_slider, Point)
        assert front.wheel_axis == front.y

    def test_kinematics(self) -> None:
        front = SuspensionRigidFrontFrameMoore("front")
        front.define_objects()
        front.define_kinematics()
        # Test if kinematics is defined
        front.steer_attachment.pos_from(front.body.masscenter)
        front.wheel_attachment.pos_from(front.body.masscenter)
        front.left_hand_grip.pos_from(front.body.masscenter)
        front.right_hand_grip.pos_from(front.body.masscenter)
        # Test velocities
        assert front.body.masscenter.vel(front.frame) == 0
        assert front.steer_attachment.vel(front.frame) == 0
        assert front.suspension_stanchions.vel(front.frame) == 0
        assert front.wheel_attachment.vel(front.frame) == front.u[0] * front.z
        assert front.suspension_slider.vel(front.frame) == front.u[0] * front.z
        assert front.left_hand_grip.vel(front.frame) == 0
        assert front.right_hand_grip.vel(front.frame) == 0

    def test_loads(self) -> None:
        front = SuspensionRigidFrontFrameMoore("front")
        front.define_all()
        loads = list(front.system.loads) + [
            act.to_loads() for act in front.system.actuators]
        assert len(loads) == 2
        if loads[0][0] == front.suspension_stanchions:
            stachion_force, slider_force = loads[0][1], loads[1][1]
        else:
            stachion_force, slider_force = loads[1][1], loads[0][1]
        q, u, k, c = front.q[0], front.u[0], front.symbols["k"], front.symbols["c"]
        stachion_force = stachion_force.xreplace({k: 1000, c: 50})
        slider_force = slider_force.xreplace({k: 1000, c: 50})
        assert stachion_force.dot(front.steer_axis).xreplace({q: 0.02, u: -0.1}) == -15
        assert slider_force.dot(front.steer_axis).xreplace({q: 0.02, u: -0.1}) == 15
        assert stachion_force.dot(front.steer_axis).xreplace({q: 0.02, u: 0.1}) == -25
        assert slider_force.dot(front.steer_axis).xreplace({q: 0.02, u: 0.1}) == 25

    @pytest.mark.skipif(PlotModel is None, reason="symmeplot not installed")
    def test_plotting(self):
        front = SuspensionRigidFrontFrameMoore("front")
        front.define_all()
        plot_model = PlotModel(front.system.frame, front.system.origin, front)
        assert len(plot_model.children) == 2
        assert any(isinstance(obj, PlotBody) for obj in plot_model.children)
        assert any(isinstance(obj, PlotLine) for obj in plot_model.children)
