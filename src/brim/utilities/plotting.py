"""Module containing utilities to easily plot the model in SymMePlot.

Notes
-----
The plotter is based on SymMePlot, which is an experimental plotting library for SymPy
mechanics. Therefore, there is no guarantee that the plotter will work in the future.

"""
from __future__ import annotations

from typing import TYPE_CHECKING

from symmeplot import SymMePlotter  # type: ignore

from brim.bicycle.front_frames import RigidFrontFrameMoore
from brim.bicycle.grounds import GroundBase
from brim.bicycle.rear_frames import RigidRearFrameMoore
from brim.bicycle.wheels import KnifeEdgeWheel
from brim.core import ModelBase, NewtonianBodyMixin

if TYPE_CHECKING:
    from symmeplot import PlotBody

__all__ = ["Plotter"]


class Plotter(SymMePlotter):
    """Plotter for models created by BRiM using symmeplot."""

    def __init__(self, ax, model: ModelBase, **inertial_frame_properties):
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

    def add_model(self, model: ModelBase, add_submodels: bool = True):
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
            body: PlotBody = self.add_body(model.body)
        if isinstance(model, RigidRearFrameMoore):
            self.add_line([model.wheel_attachment, model.steer_attachment],
                          "rear frame")
        elif isinstance(model, RigidFrontFrameMoore):
            self.add_line([model.wheel_attachment, model.steer_attachment],
                          "front frame")
        elif isinstance(model, KnifeEdgeWheel):
            body.attach_circle(model.center, model.radius, model.rotation_axis,
                               facecolor="none", edgecolor="k")
        elif isinstance(model, GroundBase):
            self.add_frame(model.frame, model.origin)
        if add_submodels:
            for submodel in model.submodels:
                self.add_model(submodel)
