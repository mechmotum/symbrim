import os

import numpy as np
import pytest
from brim.bicycle.front_frames import RigidFrontFrameMoore
from brim.bicycle.grounds import FlatGround
from brim.bicycle.pedals import SimplePedals
from brim.bicycle.rear_frames import RigidRearFrameMoore
from brim.bicycle.tyre_models import NonHolonomicTyre
from brim.bicycle.wheels import KnifeEdgeWheel
from brim.bicycle.whipple_bicycle import WhippleBicycleMoore
from brim.brim.bicycle_rider import BicycleRider
from brim.brim.pedal_connections import HolonomicPedalsConnection
from brim.brim.seat_connections import SideLeanConnection
from brim.brim.steer_connections import HolonomicSteerConnection
from brim.rider.arms import PinElbowStickLeftArm, PinElbowStickRightArm
from brim.rider.hip_joints import SphericalLeftHip, SphericalRightHip
from brim.rider.legs import TwoPinStickLeftLeg, TwoPinStickRightLeg
from brim.rider.pelvis import SimpleRigidPelvis
from brim.rider.pelvis_to_torso import FixedPelvisToTorso
from brim.rider.rider import Rider
from brim.rider.shoulder_joints import SphericalLeftShoulder, SphericalRightShoulder
from brim.rider.torso import SimpleRigidTorso
from sympy import diag
from sympy.physics.mechanics import RigidBody, msubs

try:
    from bicycleparameters import Bicycle
    from bicycleparameters.io import remove_uncertainties
    from brim.utilities.parametrize import get_inertia_vals
except ImportError:
    pytest.skip("bicycleparameters not installed", allow_module_level=True)

data_dir = os.path.join(__file__[:__file__.index("brim") + 4], "data")


def _check_dir(bicycle: str, rider: str) -> bool:
    if bicycle is not None and not os.path.isdir(
            os.path.join(data_dir, "bicycles", bicycle)):
        return False
    if rider is not None and not os.path.isdir(os.path.join(data_dir, "riders", rider)):
        return False
    if bicycle is not None and rider is not None:
        raw_data_dir = os.path.join(data_dir, "riders", rider, "RawData")
        if not (os.path.isfile(
                os.path.join(raw_data_dir, f"{rider}{bicycle}YeadonCFG.txt")) and
                os.path.isfile(
                    os.path.join(raw_data_dir, f"{rider}YeadonMeas.txt"))):
            return False
    return True


@pytest.mark.skipif(not os.path.isdir(data_dir), reason="data directory not found")
class TestParametrize:
    @pytest.mark.parametrize("bicycle, rider", [
        ("Benchmark", None),
        ("Browser", "Jason"),
    ])
    def test_find_data(self, bicycle, rider) -> None:
        # Only check whether the data that is required at a minimum for the other tests
        bike = Bicycle(bicycle, pathToData=data_dir)
        if rider is not None:
            bike.add_rider(rider)

    @pytest.fixture()
    def _setup_moore_bicycle(self) -> None:
        self.bike = WhippleBicycleMoore("bike")
        self.bike.rear_frame = RigidRearFrameMoore("rear_frame")
        self.bike.front_frame = RigidFrontFrameMoore("front_frame")
        self.bike.rear_wheel = KnifeEdgeWheel("rear_wheel")
        self.bike.rear_tyre = NonHolonomicTyre("rear_tyre")
        self.bike.front_wheel = KnifeEdgeWheel("front_wheel")
        self.bike.front_tyre = NonHolonomicTyre("front_tyre")
        self.bike.ground = FlatGround("ground")
        self.bike.define_all()

    @pytest.fixture()
    def _setup_full_model(self) -> None:
        self.bike = WhippleBicycleMoore("bicycle")
        self.bike.front_frame = RigidFrontFrameMoore("front_frame")
        self.bike.rear_frame = RigidRearFrameMoore("rear_frame")
        self.bike.front_wheel = KnifeEdgeWheel("front_wheel")
        self.bike.rear_wheel = KnifeEdgeWheel("rear_wheel")
        self.bike.front_tyre = NonHolonomicTyre("front_tyre")
        self.bike.rear_tyre = NonHolonomicTyre("rear_tyre")
        self.bike.pedals = SimplePedals("pedals")
        self.bike.ground = FlatGround("ground")

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
        self.br = BicycleRider("br")
        self.br.bicycle = self.bike
        self.br.rider = self.rider
        self.br.seat_connection = SideLeanConnection("seat_conn")
        self.br.pedal_connection = HolonomicPedalsConnection("pedals_conn")
        self.br.steer_connection = HolonomicSteerConnection("steer_conn")

        self.br.define_all()
        self.system = self.br.to_system()

    @pytest.mark.parametrize("args, kwargs, expected", [
        ([], {}, {}),
        ([1], {}, {"ixx": 1}),
        ([1, 2], {"izx": 3}, {"ixx": 1, "iyy": 2, "izx": 3}),
        ([1, 2, 3, 4, 5, 6], {},
         {"ixx": 1, "iyy": 2, "izz": 3, "ixy": 4, "iyz": 5, "izx": 6}),
        ([diag(1, 2, 3)], {},
         {"ixx": 1, "iyy": 2, "izz": 3, "ixy": 0, "iyz": 0, "izx": 0}),
        ([np.matrix([[1, 2, 3], [2, 4, 5], [3, 5, 6]])], {},
         {"ixx": 1, "iyy": 4, "izz": 6, "ixy": 2, "iyz": 5, "izx": 3}),
    ])
    def test_get_inertia_vals(self, args, kwargs, expected) -> None:
        body = RigidBody("body")
        params = get_inertia_vals(body, *args, **kwargs)
        params = {k.name[-3:]: v for k, v in params.items()}
        assert params == expected

    def test_benchmark_moore(self, _setup_moore_bicycle) -> None:
        def get_inertia_matrix(model):
            return model.body.central_inertia.to_matrix(model.body.frame)

        constants = {
            self.bike.front_wheel.symbols["r"]: 0.35,
            self.bike.rear_wheel.symbols["r"]: 0.3,
            self.bike.rear_frame.symbols["d1"]: 0.9534570696121849,
            self.bike.front_frame.symbols["d2"]: 0.2676445084476887,
            self.bike.front_frame.symbols["d3"]: 0.03207142672761929,
            self.bike.rear_frame.symbols["l1"]: 0.4707271515135145,
            self.bike.rear_frame.symbols["l2"]: -0.47792881146460797,
            self.bike.front_frame.symbols["l3"]: -0.00597083392418685,
            self.bike.front_frame.symbols["l4"]: -0.3699518200282974,
            self.bike.rear_frame.body.mass: 85.0,
            self.bike.rear_wheel.body.mass: 2.0,
            self.bike.front_frame.body.mass: 4.0,
            self.bike.front_wheel.body.mass: 3.0,
            get_inertia_matrix(self.bike.rear_wheel)[0, 0]: 0.0603,
            get_inertia_matrix(self.bike.rear_wheel)[1, 1]: 0.12,
            get_inertia_matrix(self.bike.front_wheel)[0, 0]: 0.1405,
            get_inertia_matrix(self.bike.front_wheel)[1, 1]: 0.28,
            get_inertia_matrix(self.bike.rear_frame)[0, 0]: 7.178169776497895,
            get_inertia_matrix(self.bike.rear_frame)[1, 1]: 11.0,
            get_inertia_matrix(self.bike.rear_frame)[0, 2]: 3.8225535938357873,
            get_inertia_matrix(self.bike.rear_frame)[2, 2]: 4.821830223502103,
            get_inertia_matrix(self.bike.front_frame)[0, 0]: 0.05841337700152972,
            get_inertia_matrix(self.bike.front_frame)[1, 1]: 0.06,
            get_inertia_matrix(self.bike.front_frame)[0, 2]: 0.009119225261946298,
            get_inertia_matrix(self.bike.front_frame)[2, 2]: 0.007586622998470264}
        params = self.bike.get_param_values(Bicycle("Benchmark", pathToData=data_dir))
        for sym, value in constants.items():
            assert params[sym] == pytest.approx(value, abs=1e-10)

    @pytest.mark.parametrize("bicycle, rider", [
        ("Browser", "Jason"),
        ("Rigidcl", "Luke"),
    ])
    def test_full_model_example(self, _setup_full_model, bicycle, rider) -> None:
        if not _check_dir(bicycle, rider):
            pytest.skip("data not found")
        bike_params = Bicycle(bicycle, pathToData=data_dir)
        bike_params.add_rider(rider, reCalc=True)
        bp = remove_uncertainties(bike_params.parameters["Benchmark"])
        mp = remove_uncertainties(bike_params.parameters["Measured"])
        constants = self.br.get_param_values(bike_params)
        constants.update({
            self.br.seat_connection.symbols["alpha"]: -0.7,
            self.bike.pedals.symbols["radius"]: 0.15,
            self.bike.pedals.symbols["offset"]: constants[self.rider.pelvis.symbols[
                "hip_width"]] / 2,
            self.bike.symbols["gear_ratio"]: 2.0
        })
        initial_conditions = {qi: 0 for qi in self.system.q}
        initial_conditions.update({ui: 0 for ui in self.system.u})
        initial_conditions[self.bike.q[4]] = bp["lam"]
        params = {**constants, **initial_conditions}
        assert msubs(self.bike.rear_tyre.contact_point.pos_from(
            self.bike.rear_wheel.center).magnitude(), params
                     ) == pytest.approx(bp["rR"], abs=1e-10)
        assert msubs(self.bike.front_tyre.contact_point.pos_from(
            self.bike.front_wheel.center).magnitude(), params
                     ) == pytest.approx(bp["rF"], abs=1e-10)
        assert msubs(self.bike.rear_tyre.contact_point.pos_from(
            self.bike.front_tyre.contact_point).magnitude(), params
                     ) == pytest.approx(bp["w"], abs=1e-10)
        assert msubs(self.bike.pedals.center_point.pos_from(
            self.bike.rear_wheel.center).magnitude(), params
                     ) == pytest.approx(mp["lcs"], abs=1e-10)
        assert msubs(self.bike.pedals.center_point.pos_from(
            self.bike.front_tyre.contact_point).dot(self.bike.ground.normal), params
                     ) == pytest.approx(mp["hbb"], abs=1e-10)
        assert msubs(self.bike.pedals.center_point.pos_from(
            self.bike.rear_frame.saddle).magnitude(), params
                     ) == pytest.approx(mp["lst"] + mp["lsp"], abs=1e-10)
        assert msubs(self.bike.front_frame.left_handgrip.pos_from(
            self.bike.front_frame.right_handgrip).magnitude(), params
                     ) == pytest.approx(mp["whb"], abs=1e-10)
        for hand_grip in (self.bike.front_frame.left_handgrip,
                          self.bike.front_frame.right_handgrip):
            assert msubs(hand_grip.pos_from(
                self.bike.rear_wheel.center).magnitude(), params
                         ) == pytest.approx(mp["LhbR"], abs=1e-10)
            assert msubs(hand_grip.pos_from(
                self.bike.front_wheel.center).magnitude(), params
                         ) == pytest.approx(mp["LhbF"], abs=1e-10)
