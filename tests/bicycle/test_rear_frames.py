import pytest
from brim.bicycle.rear_frames import RigidRearFrame, RigidRearFrameMoore
from brim.core import Attachment, Hub
from brim.utilities.testing import _test_descriptions
from sympy.physics.mechanics import Point, System

try:
    from brim.utilities.plotting import PlotModel
    from symmeplot import PlotBody, PlotLine
except ImportError:
    PlotModel = None


class TestRigidRearFrame:
    @pytest.mark.parametrize("base_cls, expected_cls", [
        (RigidRearFrame, RigidRearFrameMoore),
    ])
    def test_default(self, base_cls, expected_cls) -> None:
        rear = base_cls("rear")
        assert rear.name == "rear"
        assert isinstance(rear, expected_cls)

    @pytest.mark.parametrize("convention_name, base_cls, expected_cls", [
        ("moore", RigidRearFrame, RigidRearFrameMoore),
    ])
    def test_init(self, convention_name, base_cls, expected_cls) -> None:
        rear = base_cls.from_convention(convention_name, "rear")
        assert isinstance(rear, expected_cls)

    @pytest.mark.parametrize("base_cls", [RigidRearFrame])
    def test_init_error(self, base_cls) -> None:
        with pytest.raises(ValueError):
            base_cls.from_convention("not_implemented", "rear")

    @pytest.mark.parametrize("frame_cls", [RigidRearFrameMoore])
    def test_descriptions(self, frame_cls) -> None:
        _test_descriptions(frame_cls("front"))

    @pytest.mark.parametrize("cls", [RigidRearFrameMoore])
    def test_define_all(self, cls) -> None:
        rear = cls("rear")
        rear.define_all()
        assert isinstance(rear.system, System)
        assert len(rear.system.bodies) >= 1
        assert isinstance(rear.steer_hub, Hub)
        assert isinstance(rear.wheel_hub, Hub)
        assert isinstance(rear.saddle, Attachment)
        assert isinstance(rear.bottom_bracket, Point)
        for body in rear.system.bodies:
            body.masscenter.pos_from(rear.system.origin)
        for attachment in (rear.steer_hub, rear.wheel_hub, rear.saddle):
            attachment.frame.dcm(rear.system.frame)
            attachment.point.pos_from(rear.system.origin)
        rear.bottom_bracket.pos_from(rear.system.origin)

    @pytest.mark.skipif(PlotModel is None, reason="symmeplot not installed")
    @pytest.mark.parametrize("cls, n_children", [(RigidRearFrameMoore, 2)])
    def test_plotting(self, cls, n_children):
        rear = cls("rear")
        rear.define_all()
        plot_model = PlotModel(rear.system.frame, rear.system.origin, rear)
        assert len(plot_model.children) == n_children
        assert any(isinstance(obj, PlotBody) for obj in plot_model.children)
        assert any(isinstance(obj, PlotLine) for obj in plot_model.children)


class TestRigidRearFrameMoore:
    def test_default(self):
        rear = RigidRearFrameMoore("rear")
        rear.define_objects()
        rear.define_kinematics()
        assert rear.wheel_hub.axis == rear.body.y

    def test_kinematics(self):
        rear = RigidRearFrameMoore("rear")
        rear.define_objects()
        rear.define_kinematics()
        # Test velocities
        assert rear.body.masscenter.vel(rear.body.frame) == 0
        assert rear.steer_hub.point.vel(rear.body.frame) == 0
        assert rear.wheel_hub.point.vel(rear.body.frame) == 0
        assert rear.saddle.point.vel(rear.body.frame) == 0
        assert rear.bottom_bracket.vel(rear.body.frame) == 0
