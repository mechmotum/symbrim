import pytest
from brim.bicycle.front_frames import RigidFrontFrame, RigidFrontFrameMoore
from sympy.physics.mechanics import Point


class TestRigidFrontFrame:
    def test_default(self) -> None:
        front = RigidFrontFrame("front")
        assert isinstance(front, RigidFrontFrameMoore)

    @pytest.mark.parametrize("convention_name, expected_class", [
        ("moore", RigidFrontFrameMoore),
    ])
    def test_init(self, convention_name, expected_class) -> None:
        front = RigidFrontFrame.from_convention(convention_name, "front")
        assert isinstance(front, expected_class)

    def test_init_error(self) -> None:
        with pytest.raises(ValueError):
            RigidFrontFrame.from_convention("not_implemented", "front")


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
        front.left_handgrip.pos_from(front.body.masscenter)
        front.right_handgrip.pos_from(front.body.masscenter)
        # Test velocities
        assert front.body.masscenter.vel(front.frame) == 0
        assert front.steer_attachment.vel(front.frame) == 0
        assert front.wheel_attachment.vel(front.frame) == 0
        assert front.left_handgrip.vel(front.frame) == 0
        assert front.right_handgrip.vel(front.frame) == 0

    def test_descriptions(self) -> None:
        front = RigidFrontFrameMoore("front")
        front.define_objects()
        for length in front.symbols.values():
            assert front.descriptions[length] is not None
