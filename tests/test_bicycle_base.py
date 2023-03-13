from brim import BicycleBase, ModelBase


def test_bicycle_base_default():
    assert issubclass(BicycleBase, ModelBase)
