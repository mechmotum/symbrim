"""Module containing utilities to easily plot the model in SymMePlot.

Notes
-----
The plotter is based on SymMePlot, which is an experimental plotting library for SymPy
mechanics. Therefore, there is no guarantee that the plotter will work in the future.

"""
from __future__ import annotations

from typing import TYPE_CHECKING

from symmeplot import SymMePlotter

from brim.bicycle.front_frames import RigidFrontFrameMoore
from brim.bicycle.grounds import GroundBase
from brim.bicycle.pedals import PedalsBase
from brim.bicycle.rear_frames import RigidRearFrameMoore
from brim.bicycle.wheels import KnifeEdgeWheel
from brim.bicycle.whipple_bicycle import WhippleBicycleMoore
from brim.core import ConnectionBase, ModelBase, NewtonianBodyMixin
from brim.rider.arms import PinElbowStickArmMixin
from brim.rider.legs import TwoPinStickLegMixin
from brim.rider.pelvis import PelvisBase
from brim.rider.torso import TorsoBase

if TYPE_CHECKING:
    from mpl_toolkits.mplot3d.axes3d import Axes3D

__all__ = ["Plotter"]


class Plotter(SymMePlotter):
    """Plotter for models created by BRiM using symmeplot."""

    def __init__(self, ax: Axes3D, model: ModelBase, **inertial_frame_properties):
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
        self._model = model
        super().__init__(ax, model.system.frame, model.system.origin,
                         **inertial_frame_properties)
        self.add_model(model)

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
            ax_l = 0.1 * model.pedals.center_point.pos_from(
                rf.wheel_attachment).magnitude()
            saddle_low = rf.saddle.locatenew(
                "P", 0.1 * model.pedals.center_point.pos_from(rf.saddle))
            self.add_line([
                model.pedals.center_point,
                saddle_low,
                rf.wheel_attachment.locatenew("P", -ax_l / 2 * rf.wheel_axis),
                model.pedals.center_point,
                rf.wheel_attachment.locatenew("P", ax_l / 2 * rf.wheel_axis),
                saddle_low,
                rf.saddle,
                saddle_low,
                rf.steer_attachment,
                model.pedals.center_point,
            ], model.name)
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
                model.right_hip_point],
                model.name)
        elif isinstance(model, TorsoBase):
            self.add_line([
                model.body.masscenter,
                model.left_shoulder_point,
                model.right_shoulder_point,
                model.body.masscenter],
                model.name)
        if add_submodels:
            for submodel in model.submodels:
                self.add_model(submodel)
            if isinstance(model, ModelBase):
                for connection in model.connections:
                    self.add_model(connection)
