import pytest
from brim.bicycle.rear_frames import RigidRearFrame, RigidRearFrameMoore
from sympy.physics.mechanics import Point


class TestRigidRearFrame:
    def test_default(self) -> None:
        front = RigidRearFrame("rear")
        assert isinstance(front, RigidRearFrameMoore)

    @pytest.mark.parametrize("formulation_name, expected_class", [
        ("moore", RigidRearFrameMoore),
    ])
    def test_init(self, formulation_name, expected_class) -> None:
        front = RigidRearFrame("rear", formulation=formulation_name)
        assert isinstance(front, expected_class)

    def test_init_error(self) -> None:
        with pytest.raises(NotImplementedError):
            RigidRearFrame("rear", formulation="not_implemented")


class TestRigidRearFrameMoore:
    def test_default(self):
        rear = RigidRearFrameMoore("rear")
        assert rear.name == "rear"
        assert rear.frame == rear.body.frame
        assert isinstance(rear.steer_attachment, Point)
        assert isinstance(rear.wheel_attachment, Point)
        assert rear.wheel_axis == rear.y

    def test_kinematics(self):
        rear = RigidRearFrameMoore("rear")
        rear.define_kinematics()
        # Test if kinematics is defined
        rear.steer_attachment.pos_from(rear.body.masscenter)
        rear.wheel_attachment.pos_from(rear.body.masscenter)
        # Test velocities
        assert rear.body.masscenter.vel(rear.frame) == 0
        assert rear.steer_attachment.vel(rear.frame) == 0
        assert rear.wheel_attachment.vel(rear.frame) == 0

    def test_descriptions(self):
        rear = RigidRearFrameMoore("rear")
        for length in rear.lengths:
            assert rear.descriptions[length] is not None
