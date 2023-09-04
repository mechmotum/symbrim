import pytest
from brim.bicycle import (
    KnifeEdgeWheel,
    MasslessCranks,
    RigidFrontFrame,
    RigidRearFrame,
    StationaryBicycle,
    ToroidalWheel,
)


class TestStationaryBicycle:
    @pytest.fixture()
    def _setup_default(self) -> None:
        self.bike = StationaryBicycle("bicycle")
        self.bike.rear_frame = RigidRearFrame("rear_frame")

    def test_init(self) -> None:
        bicycle = StationaryBicycle("bicycle")
        assert bicycle.name == "bicycle"
        assert bicycle.front_frame is None
        assert bicycle.rear_frame is None
        assert bicycle.front_wheel is None
        assert bicycle.rear_wheel is None
        assert bicycle.cranks is None

    def test_only_rear_frame_hard(self, _setup_default):
        self.bike.define_all()

    @pytest.mark.parametrize("name, model_cls, coord_idx", [
        ("front_frame", RigidFrontFrame, (1,)),
        ("rear_wheel", KnifeEdgeWheel, (0,)),
        ("cranks", MasslessCranks, (0,)),
        ("rear_wheel", ToroidalWheel, (0,)),
    ])
    def test_optional_models(self, _setup_default, name, model_cls, coord_idx):
        setattr(self.bike, name, model_cls(name))
        self.bike.define_all()
        for idx in coord_idx:
            assert self.bike.q[idx] in self.bike.system.q
            assert self.bike.u[idx] in self.bike.system.u
            assert len(self.bike.system.kdes) == len(coord_idx)

    def test_front_wheel(self, _setup_default):
        self.bike.front_frame = RigidFrontFrame("front_frame")
        self.bike.front_wheel = KnifeEdgeWheel("front_wheel")
        self.bike.define_all()

    def test_all(self, _setup_default):
        self.bike.rear_wheel = KnifeEdgeWheel("rear_wheel")
        self.bike.cranks = MasslessCranks("cranks")
        self.bike.front_frame = RigidFrontFrame("front_frame")
        self.bike.front_wheel = KnifeEdgeWheel("front_wheel")
        self.bike.cranks = MasslessCranks("cranks")
        self.bike.define_all()
        for qi in self.bike.q:
            assert qi in self.bike.system.q
        for ui in self.bike.u:
            assert ui in self.bike.system.u
        assert len(self.bike.system.kdes) == 3

    def test_descriptions(self, _setup_default) -> None:
        self.bike.define_connections()
        self.bike.define_objects()
        for sym in self.bike.symbols.values():
            assert self.bike.descriptions[sym]
        for qi in self.bike.q:
            assert self.bike.descriptions[qi]
        for ui in self.bike.u:
            assert self.bike.descriptions[ui]
