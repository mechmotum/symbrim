"""Module containing models of the cranks."""
from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING

from sympy import Symbol
from sympy.physics.mechanics import Point, ReferenceFrame, System, Vector

from symbrim.core import ModelBase

if TYPE_CHECKING:
    import contextlib
    with contextlib.suppress(ImportError):
        from symbrim.utilities.plotting import PlotModel

__all__ = ["CranksBase"]


class CranksBase(ModelBase):
    """Base class for the cranks."""

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self._frame = ReferenceFrame(self._add_prefix("frame"))
        self._left_pedal_point = Point(self._add_prefix("LPP"))
        self._right_pedal_point = Point(self._add_prefix("RPP"))
        self._center_point = Point(self._add_prefix("CP"))
        self._system = System(self._frame, self._center_point)

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        self._left_pedal_point.set_vel(self.frame, 0)
        self._right_pedal_point.set_vel(self.frame, 0)

    @property
    def frame(self) -> ReferenceFrame:
        """Frame of the cranks."""
        return self._frame

    @property
    def center_point(self) -> Point:
        """Center point of the cranks."""
        return self._center_point

    @property
    def left_pedal_point(self) -> Point:
        """Left pedal of the bicycle."""
        return self._left_pedal_point

    @property
    def right_pedal_point(self) -> Point:
        """Right pedal of the bicycle."""
        return self._right_pedal_point

    @property
    @abstractmethod
    def rotation_axis(self) -> Vector:
        """Rotation axis of the cranks."""

    def set_plot_objects(self, plot_object: PlotModel) -> None:
        """Set the symmeplot plot objects."""
        super().set_plot_objects(plot_object)
        lp, rp, cp = (
            self.left_pedal_point, self.right_pedal_point, self.center_point)
        rot_ax = self.rotation_axis.normalize()
        ax_l = lp.pos_from(cp).dot(rot_ax) * rot_ax
        ax_r = rp.pos_from(cp).dot(rot_ax) * rot_ax
        ax_perc = 0.4
        plot_object.add_line([
            self.left_pedal_point,
            self.left_pedal_point.locatenew("P", -(1 - ax_perc) * ax_l),
            self.center_point.locatenew("P", ax_perc * ax_l),
            self.center_point.locatenew("P", ax_perc * ax_r),
            self.right_pedal_point.locatenew("P", -(1 - ax_perc) * ax_r),
            self.right_pedal_point,
        ], self.name)


class MasslessCranks(CranksBase):
    """Simplified cranks model."""

    @property
    def descriptions(self) -> dict[object, str]:
        """Descriptions of the objects."""
        return {
            **super().descriptions,
            self.symbols["radius"]: "Length of the cranks in the radial direction.",
            self.symbols["offset"]: "Distance of the pedal point from the center point "
                                    "of the cranks along the rotation axis.",
        }

    @property
    def rotation_axis(self) -> Vector:
        """Rotation axis of the cranks."""
        return self.frame.y

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self.symbols["radius"] = Symbol(self._add_prefix("radius"))
        self.symbols["offset"] = Symbol(self._add_prefix("offset"))

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        o, r = self.symbols["offset"], self.symbols["radius"]
        self.left_pedal_point.set_pos(self.center_point,
                                      -o * self.rotation_axis - r * self.frame.x)
        self.right_pedal_point.set_pos(self.center_point,
                                       o * self.rotation_axis + r * self.frame.x)
        self.left_pedal_point.set_vel(self.frame, 0)
        self.right_pedal_point.set_vel(self.frame, 0)
