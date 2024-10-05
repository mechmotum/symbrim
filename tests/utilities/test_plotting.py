from unittest.mock import MagicMock, patch

import pytest

from symbrim.rider import (
    PlanarPelvis,
    Rider,
    SphericalLeftHip,
    TwoPinLegTorque,
    TwoPinStickLeftLeg,
)

try:
    import matplotlib.pyplot as plt

    from symbrim.utilities.plotting import (
        PlotConnection,
        PlotLoadGroup,
        PlotModel,
        Plotter,
    )
except ImportError:
    pytest.skip("symmeplot not installed", allow_module_level=True)

@pytest.fixture(scope="module", autouse=True)
def mock_visualization():
    with patch("matplotlib.pyplot.subplots", return_value=(MagicMock(), MagicMock())):
        yield

class TestPlotting:
    @pytest.fixture(autouse=True)
    def _setup(self) -> None:
        self.rider = Rider("rider")
        self.rider.pelvis = PlanarPelvis("pelvis")
        self.rider.left_leg = TwoPinStickLeftLeg("left_leg")
        self.rider.left_hip = SphericalLeftHip("left_hip")
        self.load_group = TwoPinLegTorque("left_leg")
        self.rider.left_leg.add_load_groups(self.load_group)
        self.rider.define_all()
        self.fig, self.ax = plt.subplots(subplot_kw={"projection": "3d"})

    def _check_all_objects(self, plotter) -> None:
        assert isinstance(plotter, Plotter)
        assert isinstance(plotter.get_plot_object(self.rider), PlotModel)
        assert isinstance(plotter.get_plot_object(self.rider.pelvis), PlotModel)
        assert isinstance(plotter.get_plot_object(self.rider.left_leg), PlotModel)
        assert isinstance(plotter.get_plot_object(self.rider.left_hip), PlotConnection)
        assert isinstance(plotter.get_plot_object(self.load_group), PlotLoadGroup)

    def test_from_model(self) -> None:
        def find_all_pelvis_occurances(plot_object):
            if (isinstance(plot_object, PlotModel) and
                    plot_object.model is self.rider.pelvis):
                pelvis_objects.add(plot_object)
            for child in plot_object._children:
                find_all_pelvis_occurances(child)

        plotter = Plotter.from_model(self.rider)
        self._check_all_objects(plotter)
        pelvis_objects = set()
        find_all_pelvis_occurances(plotter)
        assert len(pelvis_objects) == 1

    def test_add_model(self) -> None:
        plotter = Plotter(self.rider.system.frame, self.rider.system.fixed_point)
        assert plotter.get_plot_object(self.rider) is None
        plotter.add_model(self.rider)
        self._check_all_objects(plotter)

    def test_add_load_group_manually(self) -> None:
        plotter = Plotter(self.rider.system.frame, self.rider.system.fixed_point)
        assert plotter.get_plot_object(self.rider) is None
        plotter.add_model(self.rider, plot_load_groups=False)
        assert plotter.get_plot_object(self.load_group) is None
        plotter.add_load_group(self.load_group)
        self._check_all_objects(plotter)

    @pytest.mark.parametrize("plot_load_groups", [True, False])
    def test_add_connection(self, plot_load_groups) -> None:
        plotter = Plotter(self.rider.system.frame, self.rider.system.fixed_point)
        plotter.add_connection(self.rider.left_hip, plot_load_groups=plot_load_groups)
        assert plotter.get_plot_object(self.rider) is None
        assert isinstance(plotter.get_plot_object(self.rider.pelvis), PlotModel)
        assert isinstance(plotter.get_plot_object(self.rider.left_leg), PlotModel)
        assert isinstance(plotter.get_plot_object(self.rider.left_hip), PlotConnection)
        if plot_load_groups:
            assert isinstance(plotter.get_plot_object(self.load_group), PlotLoadGroup)
