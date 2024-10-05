"""Module containing torso models."""
from __future__ import annotations

import contextlib
from abc import abstractmethod
from typing import TYPE_CHECKING

from sympy import Symbol
from sympy.physics.mechanics import Point, ReferenceFrame

from symbrim.core import ModelBase, NewtonianBodyMixin

with contextlib.suppress(ImportError):
    import numpy as np
    from yeadon.inertia import rotate_inertia

    from symbrim.utilities.parametrize import get_inertia_vals_from_yeadon

    if TYPE_CHECKING:
        from bicycleparameters import Bicycle

if TYPE_CHECKING:
    with contextlib.suppress(ImportError):
        from symbrim.utilities.plotting import PlotModel

__all__ = ["TorsoBase", "PlanarTorso"]


class TorsoBase(NewtonianBodyMixin, ModelBase):
    """Base class for the torso of a rider."""

    @property
    def left_shoulder_point(self) -> Point:
        """Location of the left shoulder.

        Explanation
        -----------
        The left shoulder point is defined as the point where the left shoulder joint
        is located. This point is used by connections to connect the left arm to the
        torso.
        """
        return self._left_shoulder_point

    @property
    @abstractmethod
    def left_shoulder_frame(self) -> ReferenceFrame:
        """The left shoulder frame.

        Explanation
        -----------
        The left shoulder frame is defined as the frame that is attached to the left
        shoulder point. This frame is used by connections to connect the left arm to
        the torso.
        """

    @property
    def right_shoulder_point(self) -> Point:
        """Location of the right shoulder.

        Explanation
        -----------
        The right shoulder point is defined as the point where the right shoulder joint
        is located. This point is used by connections to connect the right arm to the
        torso.
        """
        return self._right_shoulder_point

    @property
    @abstractmethod
    def right_shoulder_frame(self) -> ReferenceFrame:
        """The right shoulder frame.

        Explanation
        -----------
        The right shoulder frame is defined as the frame that is attached to the right
        shoulder point. This frame is used by connections to connect the right arm to
        the torso.
        """

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self._left_shoulder_point = Point(self._add_prefix("LSP"))
        self._right_shoulder_point = Point(self._add_prefix("RSP"))

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get the parameter values of the pelvis."""
        params = super().get_param_values(bicycle_parameters)
        human = bicycle_parameters.human
        if human is None:
            return params
        params[self.body.mass] = human.T.mass + human.C.mass
        return params

    def set_plot_objects(self, plot_object: PlotModel) -> None:
        """Set the symmeplot plot objects."""
        super().set_plot_objects(plot_object)
        plot_object.add_line([
            self.body.masscenter, self.left_shoulder_point, self.right_shoulder_point,
            self.body.masscenter], self.name)


class PlanarTorso(TorsoBase):
    """A planar rigid torso.

    Explanation
    -----------
    The planar rigid torso models the torso as being rigid. The shoulder joints are
    located a shoulder width apart at a height of the shoulder height above the center
    of mass of the torso.
    """

    @property
    def descriptions(self) -> dict[object, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.symbols["shoulder_width"]: "Distance between the left and right "
                                            "shoulder joints.",
            self.symbols["shoulder_height"]: "Distance between the shoulder joints and "
                                             "center of mass of the the torso.",
        }

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self.symbols["shoulder_width"] = Symbol(self._add_prefix("shoulder_width"))
        self.symbols["shoulder_height"] = Symbol(self._add_prefix("shoulder_height"))

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        w, h = self.symbols["shoulder_width"], self.symbols["shoulder_height"]
        self.left_shoulder_point.set_pos(self.body.masscenter,
                                         -w / 2 * self.y - h * self.z)
        self.right_shoulder_point.set_pos(self.body.masscenter,
                                          w / 2 * self.y - h * self.z)

    @property
    def left_shoulder_frame(self) -> ReferenceFrame:
        """The left shoulder frame."""
        return self.body.frame

    @property
    def right_shoulder_frame(self) -> ReferenceFrame:
        """The right shoulder frame."""
        return self.body.frame

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get the parameter values of the pelvis."""
        params = super().get_param_values(bicycle_parameters)
        human = bicycle_parameters.human
        if human is None:
            return params
        torso_props = human.combine_inertia(("T", "C"))
        params.update(get_inertia_vals_from_yeadon(
            self.body, rotate_inertia(human.T.rot_mat, torso_props[2])))
        params[self.symbols["shoulder_height"]] = np.linalg.norm(
            (human.A1.pos + human.B1.pos) / 2 - torso_props[1])
        params[self.symbols["shoulder_width"]] = np.linalg.norm(
            human.A1.pos - human.B1.pos)
        return params
