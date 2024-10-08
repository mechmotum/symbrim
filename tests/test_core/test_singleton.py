import pytest

from symbrim.core import Singleton


class TestSingleton:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        class TestClass(Singleton):
            pass

        self.TestClass = TestClass

    def test_singleton(self) -> None:
        assert self.TestClass() is self.TestClass()

    def test_singleton_activate(self) -> None:
        instance = self.TestClass()
        instance.deactivate()
        instance2 = self.TestClass()
        assert instance2 is self.TestClass()
        assert instance2 is not instance
        instance.activate()
        assert instance is self.TestClass()

    def test_singleton_invalid_deactivate(self) -> None:
        instance = self.TestClass()
        instance.deactivate()
        self.TestClass()
        with pytest.raises(ValueError):
            instance.deactivate()
