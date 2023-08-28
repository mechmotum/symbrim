"""Module containing utilities to easily plot the model in SymMePlot.

Notes
-----
The plotter is based on SymMePlot, which is an experimental plotting library for SymPy
mechanics. Therefore, there is no guarantee that the plotter will work in the future.

"""
from __future__ import annotations

from typing import TYPE_CHECKING

from symmeplot import SymMePlotter
from symmeplot.plot_base import PlotBase

from brim.core import ConnectionBase, LoadGroupBase, ModelBase
from brim.core.model_base import BrimBase

if TYPE_CHECKING:
    from mpl_toolkits.mplot3d.axes3d import Axes3D
    from sympy.physics.mechanics import Point, ReferenceFrame

__all__ = ["Plotter", "PlotBrimMixin", "PlotModel", "PlotConnection", "PlotLoadGroup"]


class Plotter(SymMePlotter):
    """Plotter for models created by BRiM using SymMePlot."""

    @classmethod
    def from_model(cls, ax: Axes3D, model: ModelBase, **inertial_frame_properties):
        """Initialize the plotter.

        Parameters
        ----------
        ax : mpl_toolkits.mplot3d.axes3d.Axes3D
            Axes to plot on.
        model : ModelBase
            Model to plot.
        **inertial_frame_properties
            Keyword arguments are parsed to
            :class:`symmeplot.plot_objects.PlotFrame` representing the inertial
            reference frame.
        """
        plotter = cls(ax, model.system.frame, model.system.origin,
                      **inertial_frame_properties)
        plotter._model = model
        plotter.add_model(model)
        return plotter

    def add_model(self, model: ModelBase, **kwargs):
        """Add a model to the plotter.

        Parameters
        ----------
        model : ModelBase
            Model to add.
        **kwargs : dict, optional
            Kwargs are passed to :class:`brim.utilities.plotting.PlotModel`.
        """
        self._children.append(
            PlotModel(self.inertial_frame, self.zero_point, model, **kwargs))
        return self._children[-1]


class PlotBrimMixin:
    """Mixin class for plotting BRiM objects."""

    add_point = Plotter.add_point
    add_line = Plotter.add_line
    add_vector = Plotter.add_vector
    add_frame = Plotter.add_frame
    add_body = Plotter.add_body
    plot_objects = Plotter.plot_objects
    get_plot_object = Plotter.get_plot_object

    def __init__(self, inertial_frame: ReferenceFrame, zero_point: Point,
                 brim_object: BrimBase) -> None:
        """Initialize a plot object of the BRiM model."""
        origin = None if brim_object.system is None else brim_object.system.origin
        super().__init__(inertial_frame, zero_point, origin, brim_object.name)
        self.exclude_from_init_traversal = []
        brim_object.set_plot_objects(self)
        self._expressions_self = ()

    @property
    def annot_coords(self):
        """Coordinate where the annotation text is displayed."""
        return self.origin

    def _get_expressions_to_evaluate_self(self):
        """Return a tuple of the necessary expressions for plotting."""
        return self._expressions_self

    def _update_self(self):
        """Update own artists."""
        return ()


class PlotModel(PlotBrimMixin, PlotBase):
    """Plot object of a BRiM model."""

    def __init__(self, inertial_frame: ReferenceFrame, zero_point: Point,
                 model: ModelBase, plot_submodels: bool = True,
                 plot_connections: bool = True, plot_load_groups: bool = True) -> None:
        """Initialize a plot object of a model.

        Parameters
        ----------
        inertial_frame : ReferenceFrame
            The reference frame with respect to which all objects will be oriented.
        zero_point : Point
            The absolute origin with respect to which all objects will be positioned.
        model : ModelBase
            The BRiM model, which is being plotted.
        plot_submodels : bool, optional
            Whether to plot the submodels, by default True.
        plot_connections : bool, optional
            Whether to plot the connections, by default True.
        plot_load_groups : bool, optional
            Whether to plot the load groups, by default True.
        """
        super().__init__(inertial_frame, zero_point, model)
        self.model = model
        if plot_submodels:
            for submodel in self.model.submodels:
                if submodel not in self.exclude_from_init_traversal:
                    self._children.append(PlotModel(
                        inertial_frame, zero_point, submodel,
                        plot_submodels, plot_connections, plot_load_groups))
        if plot_connections:
            for connection in self.model.connections:
                if connection not in self.exclude_from_init_traversal:
                    self._children.append(PlotConnection(
                        inertial_frame, zero_point, connection, False, plot_load_groups
                    ))
        if plot_load_groups:
            for load_group in self.model.load_groups:
                if load_group not in self.exclude_from_init_traversal:
                    self._children.append(PlotLoadGroup(
                        inertial_frame, zero_point, load_group))

    @property
    def model(self) -> ModelBase:
        """The BRiM model, which is being plotted."""
        return self._model

    @model.setter
    def model(self, model):
        if not isinstance(model, ModelBase):
            raise TypeError(f"'model' should be an instance of {ModelBase}.")
        else:
            self._model = model
            self._values = []

    @property
    def plot_submodels(self) -> tuple[PlotModel, ...]:
        """Whether to plot the submodels."""
        return tuple(self._children[:len(self.model.submodels)])


class PlotConnection(PlotBrimMixin, PlotBase):
    """Plot object of a BRiM connection."""

    def __init__(self, inertial_frame: ReferenceFrame, zero_point: Point,
                 connection: ConnectionBase, plot_submodels: bool = True,
                 plot_load_groups: bool = True) -> None:
        """Initialize a plot object of a connection.

        Parameters
        ----------
        inertial_frame : ReferenceFrame
            The reference frame with respect to which all objects will be oriented.
        zero_point : Point
            The absolute origin with respect to which all objects will be positioned.
        connection : ConnectionBase
            The BRiM connection, which is being plotted.
        plot_submodels : bool, optional
            Whether to plot the submodels, by default True.
        plot_load_groups : bool, optional
            Whether to plot the load groups, by default True.
        """
        super().__init__(inertial_frame, zero_point, connection)
        self.connection = connection
        if plot_submodels:
            for submodel in self.connection.submodels:
                if submodel not in self.exclude_from_init_traversal:
                    self._children.append(PlotModel(
                        inertial_frame, zero_point, submodel, True, True,
                        plot_load_groups))
        if plot_load_groups:
            for load_group in self.connection.load_groups:
                if load_group not in self.exclude_from_init_traversal:
                    self._children.append(PlotLoadGroup(
                        inertial_frame, zero_point, load_group))

    @property
    def connection(self) -> ConnectionBase:
        """The BRiM connection, which is being plotted."""
        return self._connection

    @connection.setter
    def connection(self, connection):
        if not isinstance(connection, ConnectionBase):
            raise TypeError(f"'connection' should be an instance of {ConnectionBase}.")
        else:
            self._connection = connection
            self._values = []

    @property
    def plot_submodels(self) -> tuple[PlotModel, ...]:
        """Whether to plot the submodels."""
        if self._children and isinstance(self._children[0], PlotModel):
            return tuple(self._children[:len(self.connection.submodels)])
        return ()


class PlotLoadGroup(PlotBrimMixin, PlotBase):
    """Plot object of a BRiM load group."""

    def __init__(self, inertial_frame: ReferenceFrame, zero_point: Point,
                 load_group: LoadGroupBase) -> None:
        """Initialize a plot object of a load group.

        Parameters
        ----------
        inertial_frame : ReferenceFrame
            The reference frame with respect to which all objects will be oriented.
        zero_point : Point
            The absolute origin with respect to which all objects will be positioned.
        load_group : LoadGroupBase
            The BRiM load group, which is being plotted.
        """
        super().__init__(inertial_frame, zero_point, load_group)
        self.load_group = load_group

    @property
    def load_group(self) -> LoadGroupBase:
        """The BRiM load group, which is being plotted."""
        return self._load_group

    @load_group.setter
    def load_group(self, load_group):
        if not isinstance(load_group, LoadGroupBase):
            raise TypeError(f"'load_group' should be an instance of {LoadGroupBase}.")
        else:
            self._load_group = load_group
            self._values = []
