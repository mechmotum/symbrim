"""Module containing utilities to easily plot the model in SymMePlot.

Notes
-----
The plotter is based on SymMePlot, which is an experimental plotting library for SymPy
mechanics. Therefore, there is no guarantee that the plotter will work in the future.

"""
from __future__ import annotations

from typing import TYPE_CHECKING, Iterable

from symmeplot import SymMePlotter
from symmeplot.plot_base import PlotBase

from brim.bicycle.front_frames import RigidFrontFrameMoore
from brim.bicycle.grounds import GroundBase
from brim.bicycle.pedals import PedalsBase
from brim.bicycle.rear_frames import RigidRearFrameMoore
from brim.bicycle.wheels import KnifeEdgeWheel
from brim.bicycle.whipple_bicycle import WhippleBicycleMoore
from brim.core import ConnectionBase, LoadGroupBase, ModelBase, NewtonianBodyMixin
from brim.core.model_base import BrimBase
from brim.rider.arms import PinElbowStickArmMixin
from brim.rider.legs import TwoPinStickLegMixin
from brim.rider.pelvis import PelvisBase
from brim.rider.pelvis_to_torso import PelvisToTorsoBase
from brim.rider.torso import TorsoBase

if TYPE_CHECKING:
    from mpl_toolkits.mplot3d.axes3d import Axes3D
    from sympy.physics.mechanics import Point, ReferenceFrame

__all__ = ["Plotter"]


class PlotBrimMixin:
    """Mixin class for plotting BRiM objects."""

    def __init__(self, inertial_frame: ReferenceFrame, zero_point: Point,
                 brim_object: BrimBase) -> None:
        """Initialize a plot object of the BRiM model."""
        origin = None if brim_object.system is None else brim_object.system.origin
        super().__init__(inertial_frame, zero_point, origin, brim_object.name)
        plot_objects = brim_object.get_plot_objects(inertial_frame, zero_point)
        if plot_objects:
            self._children.extend(plot_objects)
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
                 plot_connections: bool = True, plot_load_groups: bool = True,
                 exclude: Iterable[BrimBase] = ()) -> None:
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
        exclude : Iterable[BrimBase], optional
            BRiM child objects to exclude from plot traversal, by default ().
        """
        super().__init__(inertial_frame, zero_point, model)
        self.model = model
        if plot_submodels:
            for submodel in self.model.submodels:
                if submodel not in exclude:
                    self._children.append(PlotModel(
                        inertial_frame, zero_point, submodel,
                        plot_submodels, plot_connections, plot_load_groups))
        if plot_connections:
            for connection in self.model.connections:
                if connection not in exclude:
                    self._children.append(PlotConnection(
                        inertial_frame, zero_point, connection, False, plot_load_groups
                    ))
        if plot_load_groups:
            for load_group in self.model.load_groups:
                if load_group not in exclude:
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
                 plot_load_groups: bool = True,
                 exclude: Iterable[BrimBase] = ()) -> None:
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
        exclude : Iterable[BrimBase], optional
            BRiM child objects to exclude from plot traversal, by default ().
        """
        super().__init__(inertial_frame, zero_point, connection)
        self.connection = connection
        if plot_submodels:
            for submodel in self.connection.submodels:
                if submodel not in exclude:
                    self._children.append(PlotModel(
                        inertial_frame, zero_point, submodel, True, True,
                        plot_load_groups))
        if plot_load_groups:
            for load_group in self.connection.load_groups:
                if load_group not in exclude:
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


class Plotter(SymMePlotter):
    """Plotter for models created by BRiM using symmeplot."""

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

    def add_model(self, model: ModelBase | ConnectionBase, add_submodels: bool = True):
        """Add a model to the plotter.

        Parameters
        ----------
        model : ModelBase
            Model to add.
        add_submodels : bool, optional
            Whether to add the submodels of the model to the plot. Default is
            True.

        """
        if isinstance(model, NewtonianBodyMixin):
            body = self.add_body(model.body)
        if (isinstance(model, WhippleBicycleMoore) and add_submodels
                and model.pedals is not None):
            rf = model.rear_frame
            ax_l = 0.15 * model.pedals.center_point.pos_from(
                rf.wheel_attachment).magnitude()
            saddle_low = rf.saddle.locatenew(
                "P", 0.15 * model.pedals.center_point.pos_from(rf.saddle))
            self.add_line([
                model.pedals.center_point,
                saddle_low,
                rf.wheel_attachment.locatenew("P", -ax_l / 2 * rf.wheel_axis),
                model.pedals.center_point,
                rf.wheel_attachment.locatenew("P", ax_l / 2 * rf.wheel_axis),
                saddle_low,
                rf.saddle,
                saddle_low,
                rf.steer_attachment.locatenew(  # not perfect but close enough
                    "P", saddle_low.pos_from(rf.steer_attachment).dot(
                        rf.steer_axis) / 2 * rf.steer_axis),
                model.pedals.center_point,
            ], model.name)
            self.add_body(rf.body)
            add_submodels = False
            for submodel in model.submodels:
                if submodel is not rf:
                    self.add_model(submodel)
            for connection in model.connections:
                self.add_model(connection)
        if isinstance(model, RigidRearFrameMoore):
            self.add_line([model.wheel_attachment, model.steer_attachment],
                          model.name)
        elif isinstance(model, RigidFrontFrameMoore):
            steer_top = model.steer_attachment.locatenew(
                "P", model.steer_axis * model.left_handgrip.pos_from(
                    model.steer_attachment).dot(model.steer_axis))
            self.add_line([
                model.wheel_attachment,
                model.steer_attachment,
                steer_top,
                model.left_handgrip,
                steer_top,
                model.right_handgrip],
                model.name)
        elif isinstance(model, KnifeEdgeWheel):
            body.attach_circle(model.center, model.radius, model.rotation_axis,
                               facecolor="none", edgecolor="k")
        elif isinstance(model, GroundBase):
            self.add_frame(model.frame, model.origin)
        elif isinstance(model, PedalsBase):
            lp, rp, cp = (
                model.left_pedal_point, model.right_pedal_point, model.center_point)
            rot_ax = model.rotation_axis.normalize()
            ax_l = lp.pos_from(cp).dot(rot_ax) * rot_ax
            ax_r = rp.pos_from(cp).dot(rot_ax) * rot_ax
            ax_perc = 0.4
            self.add_line([
                model.left_pedal_point,
                model.left_pedal_point.locatenew("P", -(1 - ax_perc) * ax_l),
                model.center_point.locatenew("P", ax_perc * ax_l),
                model.center_point.locatenew("P", ax_perc * ax_r),
                model.right_pedal_point.locatenew("P", -(1 - ax_perc) * ax_r),
                model.right_pedal_point,
            ], model.name)
        elif isinstance(model, PinElbowStickArmMixin):
            self.add_line([
                model.shoulder_interpoint,
                *(joint.parent_point for joint in model.system.joints),
                model.hand_interpoint],
                model.name)
        elif isinstance(model, TwoPinStickLegMixin):
            self.add_line([
                model.hip_interpoint,
                *(joint.parent_point for joint in model.system.joints),
                model.foot_interpoint],
                model.name)
        elif isinstance(model, PelvisBase):
            self.add_line([
                model.left_hip_point,
                model.body.masscenter,
                model.right_hip_point,
                model.left_hip_point],
                model.name)
        elif isinstance(model, TorsoBase):
            self.add_line([
                model.body.masscenter,
                model.left_shoulder_point,
                model.right_shoulder_point,
                model.body.masscenter],
                model.name)
        elif isinstance(model, PelvisToTorsoBase):
            self.add_line([
                model.pelvis.body.masscenter,
                model.torso.body.masscenter],
                model.name)
        if add_submodels:
            for submodel in model.submodels:
                self.add_model(submodel)
            if isinstance(model, ModelBase):
                for connection in model.connections:
                    self.add_model(connection)
