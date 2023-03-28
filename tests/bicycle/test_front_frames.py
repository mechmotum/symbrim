import pytest
from brim.bicycle.front_frames import RigidFrontFrame, RigidFrontFrameMoore
from sympy.physics.mechanics import Point


class TestRigidFrontFrame:
    def test_default(self) -> None:
        front = RigidFrontFrame("front")
        assert isinstance(front, RigidFrontFrameMoore)

    @pytest.mark.parametrize("formulation_name, expected_class", [
        ("moore", RigidFrontFrameMoore),
    ])
    def test_init(self, formulation_name, expected_class) -> None:
        front = RigidFrontFrame("front", formulation=formulation_name)
        assert isinstance(front, expected_class)

    def test_init_error(self) -> None:
        with pytest.raises(NotImplementedError):
            RigidFrontFrame("front", formulation="not_implemented")


class TestRigidFrontFrameMoore:
    def test_default(self) -> None:
        front = RigidFrontFrameMoore("front")
        assert front.name == "front"
        assert front.frame == front.body.frame
        assert isinstance(front.steer_attachment, Point)
        assert isinstance(front.wheel_attachment, Point)
        assert front.wheel_axis == front.y

    def test_kinematics(self) -> None:
        front = RigidFrontFrameMoore("front")
        front.define_kinematics()
        # Test if kinematics is defined
        front.steer_attachment.pos_from(front.body.masscenter)
        front.wheel_attachment.pos_from(front.body.masscenter)
        # Test velocities
        assert front.body.masscenter.vel(front.frame) == 0
        assert front.steer_attachment.vel(front.frame) == 0
        assert front.wheel_attachment.vel(front.frame) == 0

    def test_descriptions(self) -> None:
        front = RigidFrontFrameMoore("front")
        for length in front.lengths:
            assert front.descriptions[length] is not None
