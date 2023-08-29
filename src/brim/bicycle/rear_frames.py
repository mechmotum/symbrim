"""Module containing the models of the rear frame of a bicycle."""
from __future__ import annotations

import contextlib
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from sympy import Symbol, symbols
from sympy.physics.mechanics import Point, Vector, inertia

from brim.core import (
    ModelBase,
    NewtonianBodyMixin,
    set_default_convention,
)

with contextlib.suppress(ImportError):
    import numpy as np
    from bicycleparameters.io import remove_uncertainties
    from bicycleparameters.main import calculate_benchmark_from_measured
    from bicycleparameters.rider import yeadon_vec_to_bicycle_vec
    from dtk.bicycle import benchmark_to_moore

    from brim.utilities.parametrize import get_inertia_vals

    if TYPE_CHECKING:
        from bicycleparameters import Bicycle

if TYPE_CHECKING:
    with contextlib.suppress(ImportError):
        from brim.utilities.plotting import PlotModel

__all__ = ["RearFrameBase", "RigidRearFrame", "RigidRearFrameMoore"]


class RearFrameBase(NewtonianBodyMixin, ModelBase):
    """Base class for the rear frame of a bicycle."""

    @property
    @abstractmethod
    def steer_axis(self) -> Vector:
        """Steer axis expressed in the rear frame."""

    @property
    @abstractmethod
    def wheel_axis(self) -> Vector:
        """Wheel axis expressed in the rear frame."""

    @property
    @abstractmethod
    def saddle(self) -> Point:
        """Point representing the saddle."""

    @property
    @abstractmethod
    def bottom_bracket(self) -> Point:
        """Point representing the center of the bottom bracket."""

    @property
    @abstractmethod
    def wheel_attachment(self) -> Point:
        """Point representing attachment of the rear wheel."""

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get the parameter values of the rear frame."""
        params = super().get_param_values(bicycle_parameters)
        bp = remove_uncertainties(bicycle_parameters.parameters.get(
            "Measured", bicycle_parameters.parameters.get("Benchmark")))
        if bp is not None:
            if hasattr(bp["mB"], "nominal_value"):
                params[self.body.mass] = bp["mB"].nominal_value
            else:
                params[self.body.mass] = bp["mB"]
        return params


@set_default_convention("moore")
class RigidRearFrame(RearFrameBase):
    """Rigid rear frame."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Dictionary of descriptions of the rear frame's symbols."""
        return {
            **super().descriptions,
            self.symbols["l_bbx"]: f"Distance between the rear hub and the bottom "
                                   f"bracket along {self.x}.",
            self.symbols["l_bbz"]: f"Distance between the rear hub and the bottom "
                                   f"bracket along {self.z}.",
        }

    def _define_objects(self):
        """Define the objects of the rear frame."""
        super()._define_objects()
        self.body.central_inertia = inertia(self.body.frame,
                                            *symbols(self._add_prefix("ixx iyy izz")),
                                            izx=Symbol(self._add_prefix("izx")))
        self._wheel_attachment = Point(self._add_prefix("wheel_attachment"))
        self._saddle = Point(self._add_prefix("saddle"))
        self._bottom_bracket = Point(self._add_prefix("bottom_bracket"))
        self.symbols.update({name: Symbol(self._add_prefix(name))
                             for name in ("l_bbx", "l_bbz")})

    def _define_kinematics(self):
        """Define the kinematics of the rear frame."""
        super()._define_kinematics()
        self.wheel_attachment.set_vel(self.frame, 0)
        self.saddle.set_vel(self.frame, 0)
        self.bottom_bracket.set_pos(self.wheel_attachment,
                                    self.symbols["l_bbx"] * self.x +
                                    self.symbols["l_bbz"] * self.z)
        self.bottom_bracket.set_vel(self.frame, 0)

    def _define_loads(self):
        """Define the loads acting upon the rear frame."""
        super()._define_loads()

    @property
    @abstractmethod
    def steer_axis(self) -> Vector:
        """Steer axis expressed in the rear frame."""

    @property
    def wheel_axis(self) -> Vector:
        """Wheel axis expressed in the rear frame."""
        return self.body.y

    @property
    def wheel_attachment(self) -> Point:
        """Point representing attachment of the rear wheel."""
        return self._wheel_attachment

    @property
    def saddle(self) -> Point:
        """Point representing the saddle."""
        return self._saddle

    @property
    def bottom_bracket(self) -> Point:
        """Point representing the center of the bottom bracket."""
        return self._bottom_bracket

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get a parameters mapping of a model based on a bicycle parameters object."""
        params = super().get_param_values(bicycle_parameters)
        if "Benchmark" in bicycle_parameters.parameters:
            bp = remove_uncertainties(bicycle_parameters.parameters["Benchmark"])
        if "Measured" in bicycle_parameters.parameters:
            mep = remove_uncertainties(bicycle_parameters.parameters["Measured"])
            rr, lcs, hbb, lamht = (mep.get(name) for name in (
                "rR", "lcs", "hbb", "lamht"))
            if rr is None and "Benchmark" in bicycle_parameters.parameters:
                rr = bp["rR"]
            if lamht is None and "Benchmark" in bicycle_parameters.parameters:
                lamht = np.pi / 2 - bp["lam"]
            if not any(value is None for value in (rr, lcs, hbb, lamht)):
                glob_z = rr - hbb
                glob_x = np.sqrt(lcs ** 2 - glob_z ** 2)
                params[self.symbols["l_bbx"]] = (
                        glob_x * np.sin(lamht) - glob_z * np.cos(lamht))
                params[self.symbols["l_bbz"]] = (
                        glob_x * np.cos(lamht) + glob_z * np.sin(lamht))
        return params


class RigidRearFrameMoore(RigidRearFrame):
    """Rigid rear frame model based on Moore's convention."""

    convention: str = "moore"

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the rear frame."""
        return {
            **super().descriptions,
            self.symbols["d1"]: "Perpendicular distance from the steer axis to the "
                                "center of the rear wheel (rear offset).",
            self.symbols["l1"]: "Distance in the rear frame x direction from the rear "
                                "wheel center to the center of mass of the rear frame.",
            self.symbols["l2"]: "Distance in the rear frame z direction from the rear "
                                "wheel center to the center of mass of the rear frame.",
            self.symbols["d4"]: "Distance in the rear frame x direction from the rear "
                                "wheel center to the point representing the saddle.",
            self.symbols["d5"]: "Distance in the rear frame z direction from the rear "
                                "wheel center to the point representing the saddle.",
        }

    def _define_objects(self):
        """Define the objects of the rear frame."""
        super()._define_objects()
        self.symbols.update({
            name: Symbol(self._add_prefix(name)) for name in ("d1", "l1", "l2", "d4",
                                                              "d5")})
        self._steer_attachment = Point("steer_attachment")

    def _define_kinematics(self):
        """Define the kinematics of the rear frame."""
        super()._define_kinematics()
        d1, l1, l2, d4, d5 = (self.symbols[name] for name in ("d1", "l1", "l2", "d4",
                                                              "d5"))
        self.steer_attachment.set_pos(self.wheel_attachment, d1 * self.x)
        self.body.masscenter.set_pos(self.wheel_attachment, l1 * self.x + l2 * self.z)
        self.saddle.set_pos(self.wheel_attachment, d4 * self.x + d5 * self.z)
        self.body.masscenter.set_vel(self.frame, 0)
        self.steer_attachment.set_vel(self.frame, 0)
        self.wheel_attachment.set_vel(self.frame, 0)
        self.saddle.set_vel(self.frame, 0)

    @property
    def steer_axis(self) -> Vector:
        """Steer axis expressed in the rear frame."""
        return self.z

    @property
    def steer_attachment(self) -> Point:
        """Attachment point between the rear frame and the front frame.

        Explanation
        -----------
        In Moore's convention an attachment point between the rear and the front frame
        is defined. This point is defined as the intersection of the steer axis a
        perpendicular line, which passes through the attachment of the rear wheel to the
        rear frame.
        """
        return self._steer_attachment

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get the parameter values of the rear frame."""
        params = super().get_param_values(bicycle_parameters)
        if "Benchmark" in bicycle_parameters.parameters:
            if bicycle_parameters.hasRider:
                bp = remove_uncertainties(calculate_benchmark_from_measured(
                    bicycle_parameters.parameters["Measured"])[0])
            else:
                bp = remove_uncertainties(bicycle_parameters.parameters["Benchmark"])
            mop = benchmark_to_moore(bp)
            params[self.body.mass] = mop["mc"]
            params.update(get_inertia_vals(
                self.body, mop["ic11"], mop["ic22"], mop["ic33"], mop["ic12"],
                mop["ic23"], mop["ic31"]))
            params[self.symbols["d1"]] = mop["d1"]
            params[self.symbols["l1"]] = mop["l1"]
            params[self.symbols["l2"]] = mop["l2"]
        if "Measured" in bicycle_parameters.parameters:
            mep = remove_uncertainties(bicycle_parameters.parameters["Measured"])
            rr, lcs, hbb, lst, lsp, lamst, lamht = (mep.get(name) for name in (
                "rR", "lcs", "hbb", "lst", "lsp", "lamst", "lamht"))
            if rr is None and "Benchmark" in bicycle_parameters.parameters:
                rr = bp["rR"]
            if lamht is None and "Benchmark" in bicycle_parameters.parameters:
                lamht = np.pi / 2 - bp["lam"]
            if not any(value is None for value in (rr, lcs, hbb, lst, lsp, lamst)):
                r_rc_sdl = (yeadon_vec_to_bicycle_vec(
                    np.matrix([[0], [0], [0]]), mep, bp) + np.matrix([[0], [0], [rr]]))
                params[self.symbols["d4"]] = (
                        r_rc_sdl[0, 0] * np.sin(lamht) - r_rc_sdl[2, 0] * np.cos(lamht))
                params[self.symbols["d5"]] = (
                        r_rc_sdl[0, 0] * np.cos(lamht) + r_rc_sdl[2, 0] * np.sin(lamht))
        return params

    def set_plot_objects(self, plot_object: PlotModel) -> None:
        """Set the symmeplot plot objects."""
        super().set_plot_objects(plot_object)
        ax_l = 0.15 * self.bottom_bracket.pos_from(
            self.wheel_attachment).magnitude()
        saddle_low = self.saddle.locatenew(
            "P", 0.15 * self.bottom_bracket.pos_from(self.saddle))
        points = [
            self.bottom_bracket,
            saddle_low,
            self.wheel_attachment.locatenew("P", -ax_l / 2 * self.wheel_axis),
            self.bottom_bracket,
            self.wheel_attachment.locatenew("P", ax_l / 2 * self.wheel_axis),
            saddle_low,
            self.saddle,
            saddle_low,
            self.steer_attachment.locatenew(  # not perfect but close enough
                "P", saddle_low.pos_from(self.steer_attachment).dot(
                    self.steer_axis) / 2 * self.steer_axis),
            self.bottom_bracket,
        ]
        plot_object.add_line(points, self.name)
