import pytest
from brim.bicycle.rear_frames import RigidRearFrame, RigidRearFrameMoore
from sympy.physics.mechanics import Point

try:
    from brim.utilities.plotting import PlotModel
    from symmeplot import PlotBody, PlotLine
except ImportError:
    PlotModel = None


class TestRigidRearFrame:
    def test_default(self) -> None:
        front = RigidRearFrame("rear")
        assert isinstance(front, RigidRearFrameMoore)

    @pytest.mark.parametrize("convention_name, expected_class", [
        ("moore", RigidRearFrameMoore),
    ])
    def test_init(self, convention_name, expected_class) -> None:
        front = RigidRearFrame.from_convention(convention_name, "rear")
        assert isinstance(front, expected_class)

    def test_init_error(self) -> None:
        with pytest.raises(ValueError):
            RigidRearFrame.from_convention("not_implemented", "rear")


class TestRigidRearFrameMoore:
    def test_default(self):
        rear = RigidRearFrameMoore("rear")
        rear.define_objects()
        assert rear.name == "rear"
        assert rear.frame == rear.body.frame
        assert isinstance(rear.steer_attachment, Point)
        assert isinstance(rear.wheel_attachment, Point)
        assert isinstance(rear.saddle, Point)
        assert isinstance(rear.bottom_bracket, Point)
        assert rear.wheel_axis == rear.y

    def test_kinematics(self):
        rear = RigidRearFrameMoore("rear")
        rear.define_objects()
        rear.define_kinematics()
        # Test if kinematics is defined
        rear.steer_attachment.pos_from(rear.body.masscenter)
        rear.wheel_attachment.pos_from(rear.body.masscenter)
        rear.saddle.pos_from(rear.body.masscenter)
        # Test velocities
        assert rear.body.masscenter.vel(rear.frame) == 0
        assert rear.steer_attachment.vel(rear.frame) == 0
        assert rear.wheel_attachment.vel(rear.frame) == 0
        assert rear.saddle.vel(rear.frame) == 0
        assert rear.bottom_bracket.vel(rear.frame) == 0

    def test_descriptions(self):
        rear = RigidRearFrameMoore("rear")
        rear.define_objects()
        for length in rear.symbols.values():
            assert rear.descriptions[length] is not None

    @pytest.mark.skipif(PlotModel is None, reason="symmeplot not installed")
    def test_plotting(self):
        rear = RigidRearFrameMoore("rear")
        rear.define_all()
        plot_model = PlotModel(rear.system.frame, rear.system.origin, rear)
        assert len(plot_model.children) == 2
        assert any(isinstance(obj, PlotBody) for obj in plot_model.children)
        assert any(isinstance(obj, PlotLine) for obj in plot_model.children)
