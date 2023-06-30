from __future__ import annotations

import pytest
from brim.bicycle.rear_frames import RigidRearFrameMoore
from brim.brim.base_connections import SeatBase
from brim.brim.seat_connections import SideLeanSeat
from brim.rider.pelvis import PlanarPelvis
from brim.utilities.testing import _test_descriptions, create_model_of_connection
from sympy import simplify, zeros
from sympy.physics.mechanics import ReferenceFrame


@pytest.mark.parametrize("seat_cls", [SideLeanSeat])
class TestSeatConnectionBase:
    @pytest.fixture(autouse=True)
    def _setup(self, seat_cls) -> None:
        self.model = create_model_of_connection(seat_cls)("model")
        self.model.pelvis = PlanarPelvis("pelvis")
        self.model.rear_frame = RigidRearFrameMoore("rear_frame")
        self.model.conn = seat_cls("seat_connection")
        self.model.define_connections()
        self.model.define_objects()
        self.model.define_kinematics()
        self.model.define_loads()
        self.model.define_constraints()

    def test_types(self) -> None:
        assert isinstance(self.model.conn, SeatBase)

    def test_descriptions(self) -> None:
        _test_descriptions(self.model.conn)


class TestSideLeanConnection:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.model = create_model_of_connection(SideLeanSeat)("model")
        self.model.pelvis = PlanarPelvis("pelvis")
        self.model.rear_frame = RigidRearFrameMoore("rear_frame")
        self.model.conn = SideLeanSeat("seat_connection")
        self.pelvis, self.rear_frame, self.conn = (
            self.model.pelvis, self.model.rear_frame, self.model.conn)

    def test_default(self) -> None:
        self.model.define_all()
        a = self.conn.symbols["alpha"]
        int_frame = ReferenceFrame("int_frame")
        int_frame.orient_axis(self.rear_frame.frame, a, self.rear_frame.y)
        assert simplify(self.conn.frame_lean_axis.to_matrix(self.rear_frame.frame) -
                        int_frame.x.to_matrix(self.rear_frame.frame)) == zeros(3, 1)
        assert self.conn.pelvis_lean_axis == self.pelvis.x
        assert self.pelvis.body.masscenter.pos_from(
            self.rear_frame.saddle) == (
                -self.pelvis.symbols["com_height"] * self.pelvis.z)

    def test_set_frame_lean_axis(self) -> None:
        self.model.define_connections()
        self.model.define_objects()
        with pytest.raises(ValueError):
            self.conn.frame_lean_axis = self.pelvis.x
        self.conn.frame_lean_axis = self.rear_frame.y
        assert self.conn.frame_lean_axis == self.rear_frame.y
        self.model.define_kinematics()
        assert self.pelvis.frame.ang_vel_in(self.rear_frame.frame).dot(
            self.rear_frame.y) == self.conn.u

    def test_set_pelvis_lean_axis(self) -> None:
        self.model.define_connections()
        self.model.define_objects()
        with pytest.raises(ValueError):
            self.conn.pelvis_lean_axis = self.rear_frame.x
        self.conn.pelvis_lean_axis = self.pelvis.y
        assert self.conn.pelvis_lean_axis == self.pelvis.y
        self.model.define_kinematics()
        assert self.pelvis.frame.ang_vel_in(self.rear_frame.frame).dot(
            self.pelvis.y) == self.conn.u

    @pytest.mark.parametrize("as_point", [True, False])
    def test_set_pelvis_interpoint(self, as_point) -> None:
        self.model.define_connections()
        self.model.define_objects()
        p = self.rear_frame.x
        if as_point:
            p = self.rear_frame.saddle.locatenew("P", p)
        with pytest.raises(ValueError):
            self.conn.pelvis_interpoint = p
        p = v = self.pelvis.z
        if as_point:
            p = self.pelvis.body.masscenter.locatenew("P", v)
        self.conn.pelvis_interpoint = p
        assert self.conn.pelvis_interpoint == p
        self.model.define_kinematics()
        assert self.pelvis.body.masscenter.pos_from(self.rear_frame.saddle) == -v
