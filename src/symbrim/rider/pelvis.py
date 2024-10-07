"""Module containing pelvis models."""
from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from sympy import Symbol
from sympy.physics.mechanics import Point

from symbrim.core import ModelBase, NewtonianBodyMixin

with contextlib.suppress(ImportError):
    import numpy as np

    from symbrim.utilities.parametrize import get_inertia_vals_from_yeadon

    if TYPE_CHECKING:
        from bicycleparameters import Bicycle

if TYPE_CHECKING:
    with contextlib.suppress(ImportError):
        from symbrim.utilities.plotting import PlotModel

__all__ = ["PelvisBase", "PlanarPelvis"]


class PelvisBase(NewtonianBodyMixin, ModelBase):
    """Base class for the pelvis of a rider."""

    @property
    def left_hip_point(self) -> Point:
        """Location of the left hip.

        Explanation
        -----------
        The left hip point is defined as the point where the left hip joint is located.
        This point is used by connections to connect the left leg to the pelvis.
        """
        return self._left_hip_point

    @property
    def right_hip_point(self) -> Point:
        """Location of the right hip.

        Explanation
        -----------
        The right hip point is defined as the point where the right hip joint is
        located. This point is used by connections to connect the right leg to the
        pelvis.
        """
        return self._right_hip_point

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self._left_hip_point = Point(self._add_prefix("LHP"))
        self._right_hip_point = Point(self._add_prefix("RHP"))

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get the parameter values of the pelvis."""
        params = super().get_param_values(bicycle_parameters)
        human = bicycle_parameters.human
        if human is None:
            return params
        params[self.body.mass] = human.P.mass
        return params

    def set_plot_objects(self, plot_object: PlotModel) -> None:
        """Set the symmeplot plot objects."""
        super().set_plot_objects(plot_object)
        plot_object.add_line([
            self.left_hip_point, self.body.masscenter, self.right_hip_point,
            self.left_hip_point], self.name)


class PlanarPelvis(PelvisBase):
    """A planar rigid pelvis.

    Explanation
    -----------
    The planar rigid pelvis models the pelvis as being a rigid body. The hip joints are
    located a hip width apart from each other with the center of mass at the center.
    """

    @property
    def descriptions(self) -> dict[object, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.symbols["hip_width"]: "Distance between the left and right hip"
                                       "points.",
            self.symbols["com_height"]: "Distance along the z axis between the center "
                                        "of mass and the hip joints.",
        }

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self.symbols["hip_width"] = Symbol(self._add_prefix("hip_width"))
        self.symbols["com_height"] = Symbol(self._add_prefix("com_height"))

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        self.left_hip_point.set_pos(self.body.masscenter,
                                    -self.symbols["hip_width"] * self.y / 2 +
                                    self.symbols["com_height"] * self.z)
        self.right_hip_point.set_pos(self.body.masscenter,
                                     self.symbols["hip_width"] * self.y / 2 +
                                     self.symbols["com_height"] * self.z)

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get the parameter values of the pelvis."""
        params = super().get_param_values(bicycle_parameters)
        human = bicycle_parameters.human
        if human is None:
            return params
        params.update(get_inertia_vals_from_yeadon(self.body, human.P.rel_inertia))
        params[self.symbols["com_height"]] = human.P.rel_center_of_mass[2, 0]
        params[self.symbols["hip_width"]] = np.linalg.norm(human.J1.pos - human.K1.pos)
        return params
