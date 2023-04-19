from __future__ import annotations

import pytest
from brim.rider import (
    FixedPelvisToTorso,
    PinElbowStickLeftArm,
    PinElbowStickRightArm,
    Rider,
    SimpleRigidPelvis,
    SimpleRigidTorso,
    SphericalLeftHip,
    SphericalLeftShoulder,
    SphericalRightHip,
    SphericalRightShoulder,
    TwoPinStickLeftLeg,
    TwoPinStickRightLeg,
)
from brim.utilities import to_system


class TestCompleteRider:
    @pytest.fixture()
    def _setup(self) -> None:
        self.rider = Rider("rider")
        self.rider.pelvis = SimpleRigidPelvis("pelvis")
        self.rider.torso = SimpleRigidTorso("torso")
        self.rider.left_arm = PinElbowStickLeftArm("left_arm")
        self.rider.right_arm = PinElbowStickRightArm("right_arm")
        self.rider.left_leg = TwoPinStickLeftLeg("left_leg")
        self.rider.right_leg = TwoPinStickRightLeg("right_leg")
        self.rider.pelvis_to_torso = FixedPelvisToTorso("pelvis_to_torso")
        self.rider.left_hip = SphericalLeftHip("left_hip")
        self.rider.right_hip = SphericalRightHip("right_hip")
        self.rider.left_shoulder = SphericalLeftShoulder("left_shoulder")
        self.rider.right_shoulder = SphericalRightShoulder("right_shoulder")

    def test_setup(self, _setup) -> None:
        assert self.rider.pelvis is not None
        assert self.rider.torso is not None
        assert self.rider.left_arm is not None
        assert self.rider.right_arm is not None
        assert self.rider.left_leg is not None
        assert self.rider.right_leg is not None
        assert self.rider.pelvis_to_torso is not None
        assert self.rider.left_hip is not None
        assert self.rider.right_hip is not None
        assert self.rider.left_shoulder is not None
        assert self.rider.right_shoulder is not None
        self.rider.define_all()

    def test_minimal(self) -> None:
        rider = Rider("rider")
        with pytest.raises(Exception):
            rider.define_all()
        rider.pelvis = SimpleRigidPelvis("pelvis")
        rider.define_all()

    def test_form_eoms(self, _setup) -> None:
        self.rider.define_all()
        system = to_system(self.rider)
        system.validate_system()
        system.form_eoms()
