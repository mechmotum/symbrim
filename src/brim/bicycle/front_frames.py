"""Module containing the models of the front frame of a bicycle."""
from __future__ import annotations

import contextlib
from abc import abstractmethod
from typing import TYPE_CHECKING, Any

from sympy import ImmutableMatrix as Matrix
from sympy import Symbol, symbols
from sympy.physics.mechanics import Force, Point, Vector, dynamicsymbols, inertia

from brim.core import ModelBase, NewtonianBodyMixin, set_default_convention

with contextlib.suppress(ImportError):
    import numpy as np
    from bicycleparameters.io import remove_uncertainties
    from dtk.bicycle import benchmark_to_moore
    from scipy.optimize import fsolve

    from brim.utilities.parametrize import get_inertia_vals

    if TYPE_CHECKING:
        from bicycleparameters import Bicycle

if TYPE_CHECKING:
    with contextlib.suppress(ImportError):
        from brim.utilities.plotting import PlotModel

__all__ = ["FrontFrameBase", "RigidFrontFrame", "RigidFrontFrameMoore",
           "SuspensionRigidFrontFrame", "SuspensionRigidFrontFrameMoore"]


class FrontFrameBase(NewtonianBodyMixin, ModelBase):
    """Base class for the front frame of a bicycle."""

    def _define_objects(self):
        """Define the objects of the front frame."""
        super()._define_objects()
        self._wheel_attachment = Point(self._add_prefix("wheel_attachment"))
        self._left_hand_grip = Point(self._add_prefix("left_hand_grip"))
        self._right_hand_grip = Point(self._add_prefix("right_hand_grip"))

    @property
    @abstractmethod
    def steer_axis(self) -> Vector:
        """Steer axis expressed in the front frame."""

    @property
    @abstractmethod
    def wheel_axis(self) -> Vector:
        """Wheel axis expressed in the front frame."""

    @property
    def wheel_attachment(self) -> Point:
        """Point representing the attachment of the front wheel."""
        return self._wheel_attachment

    @property
    def left_hand_grip(self) -> Point:
        """Point representing the left hand grip."""
        return self._left_hand_grip

    @property
    def right_hand_grip(self) -> Point:
        """Point representing the right hand grip."""
        return self._right_hand_grip

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get the parameter values of the front frame."""
        params = super().get_param_values(bicycle_parameters)
        bp = remove_uncertainties(bicycle_parameters.parameters.get(
            "Benchmark", bicycle_parameters.parameters.get("Measured")))
        if bp is not None:
            if hasattr(bp["mH"], "nominal_value"):
                params[self.body.mass] = bp["mH"].nominal_value
            else:
                params[self.body.mass] = bp["mH"]
        return params


@set_default_convention("moore")
class RigidFrontFrame(FrontFrameBase):
    """Rigid front frame."""

    def _define_objects(self):
        """Define the objects of the front frame."""
        super()._define_objects()
        self.body.central_inertia = inertia(self.body.frame,
                                            *symbols(self._add_prefix("ixx iyy izz")),
                                            izx=Symbol(self._add_prefix("izx")))

    def _define_kinematics(self) -> None:
        """Define the kinematics of the front frame."""
        self.body.masscenter.set_vel(self.frame, 0)
        self.wheel_attachment.set_vel(self.frame, 0)
        self.left_hand_grip.set_vel(self.frame, 0)
        self.right_hand_grip.set_vel(self.frame, 0)


class RigidFrontFrameMoore(RigidFrontFrame):
    """Rigid front frame model based on Moore's convention."""

    convention: str = "moore"

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the front frame."""
        return {
            **super().descriptions,
            self.symbols["d2"]: "Distance between wheels along the steer axis.",
            self.symbols["d3"]: "Perpendicular distance from the steer axis to the "
                                "center of the front wheel (fork offset).",
            self.symbols["l3"]: "Distance in the front frame x direction from the front"
                                " wheel center to the center of mass of the front "
                                "frame.",
            self.symbols["l4"]: "Distance in the front frame z direction from the front"
                                " wheel center to the center of mass of the front "
                                "frame.",
            self.symbols["d6"]: "Perpendicular distance from the steer axis to the "
                                "hand grips. The hand grips are in front of the steer "
                                "axis if d6 is positive.",
            self.symbols["d7"]: "Half of the distance between the hand grips.",
            self.symbols["d8"]: "Distance of the hand grips from the steer point along "
                                "the steer axis. The hand grips are below the steer "
                                "attachment if d8 is positive.",
        }

    def _define_objects(self):
        """Define the objects of the front frame."""
        super()._define_objects()
        self.symbols.update({
            name: Symbol(self._add_prefix(name)) for name in ("d2", "d3", "l3", "l4",
                                                              "d6", "d7", "d8")})
        self._steer_attachment = Point(self._add_prefix("steer_attachment"))

    def _define_kinematics(self):
        """Define the kinematics of the front frame."""
        super()._define_kinematics()
        d2, d3, l3, l4, d6, d7, d8 = (self.symbols[name] for name in (
            "d2", "d3", "l3", "l4", "d6", "d7", "d8"))
        self.wheel_attachment.set_pos(self.steer_attachment, d3 * self.x + d2 * self.z)
        self.body.masscenter.set_pos(self.wheel_attachment, l3 * self.x + l4 * self.z)
        self.left_hand_grip.set_pos(self.steer_attachment,
                                    d6 * self.x - d7 * self.y + d8 * self.z)
        self.right_hand_grip.set_pos(self.steer_attachment,
                                     d6 * self.x + d7 * self.y + d8 * self.z)
        self.steer_attachment.set_vel(self.frame, 0)

    @property
    def steer_axis(self) -> Vector:
        """Steer axis expressed in the front frame."""
        return self.body.z

    @property
    def wheel_axis(self) -> Vector:
        """Wheel axis expressed in the front frame."""
        return self.body.y

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
        """Get the parameter values of the front frame."""
        params = super().get_param_values(bicycle_parameters)
        str_params = _get_front_frame_moore_params(bicycle_parameters)
        if "mass" in str_params:
            params[self.body.mass] = str_params["mass"]
        if "inertia_vals" in str_params:
            params.update(get_inertia_vals(self.body, *str_params["inertia_vals"]))
        for name in ("d2", "d3", "l3", "l4", "d6", "d7", "d8"):
            if name in str_params:
                params[self.symbols[name]] = str_params[name]
        return params

    def set_plot_objects(self, plot_object: PlotModel) -> None:
        """Set the symmeplot plot objects."""
        super().set_plot_objects(plot_object)
        steer_top = self.steer_attachment.locatenew(
            "P", self.steer_axis * self.left_hand_grip.pos_from(
                self.steer_attachment).dot(self.steer_axis))
        plot_object.add_line([
            self.wheel_attachment, self.steer_attachment, steer_top,
            self.left_hand_grip, steer_top, self.right_hand_grip], self.name)


@set_default_convention("moore")
class SuspensionRigidFrontFrame(FrontFrameBase):
    """Front frame with suspension and no structural flexibility."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the front frame."""
        return {
            **super().descriptions,
            self.q[0]: "Compression of the front suspension.",
            self.u[0]: "Compression velocity of the front suspension.",
            self.symbols["k"]: "Spring stiffness of the front suspension.",
            self.symbols["c"]: "Damping coefficient of the front suspension.",
        }

    def _define_objects(self) -> None:
        """Define the objects of the front frame."""
        super()._define_objects()
        self.q = Matrix([dynamicsymbols(self._add_prefix("q"))])
        self.u = Matrix([dynamicsymbols(self._add_prefix("u"))])
        self.symbols["k"] = Symbol(self._add_prefix("k"))
        self.symbols["c"] = Symbol(self._add_prefix("c"))


class SuspensionRigidFrontFrameMoore(SuspensionRigidFrontFrame):
    """Front frame with suspension and no structural flexibility.

    Explanation
    -----------
    The front frame is modeled as a rigid body with a suspension. The suspension is
    modeled as a spring-damper system. The forces are applied parallel to the steer
    axis with at a parametrized distance ``symbols["d9"]`` from the steer axis.
    """

    convention: str = "moore"

    @property
    def descriptions(self) -> dict[Any, str]:
        """Descriptions of the attributes of the front frame."""
        return {
            **super().descriptions,
            self.symbols["d2"]: f"Distance between wheels along the steer axis when "
                                f"{self.q[0]} is zero.",
            self.symbols["d3"]: "Perpendicular distance from the steer axis to the "
                                "center of the front wheel (fork offset).",
            self.symbols["l3"]: "Distance in the front frame x direction from the front"
                                " wheel center to the center of mass of the front "
                                "frame.",
            self.symbols["l4"]: f"Distance in the front frame z direction from the "
                                f"front wheel center to the center of mass of the front"
                                f" frame when {self.q[0]} is zero.",
            self.symbols["d6"]: "Perpendicular distance from the steer axis to the "
                                "hand grips. The hand grips are in front of the steer "
                                "axis if d6 is positive.",
            self.symbols["d7"]: "Half of the distance between the hand grips.",
            self.symbols["d8"]: "Distance of the hand grips from the steer point along "
                                "the steer axis. The hand grips are below the steer "
                                "attachment if d8 is positive.",
            self.symbols["d9"]: "Perpendicular distance from the steer axis to the"
                                "suspension.",
        }

    def _define_objects(self):
        """Define the objects of the front frame."""
        super()._define_objects()
        self.symbols.update({
            name: Symbol(self._add_prefix(name)) for name in ("d2", "d3", "l3", "l4",
                                                              "d6", "d7", "d8", "d9")})
        self._steer_attachment = Point(self._add_prefix("steer_attachment"))
        self._suspension_stanchions = Point(self._add_prefix("suspension_stanchions"))
        self._suspension_slider = Point(self._add_prefix("suspension_slider"))

    def _define_kinematics(self):
        """Define the kinematics of the front frame."""
        super()._define_kinematics()
        d2, d3, l3, l4, d6, d7, d8, d9 = (self.symbols[name] for name in (
            "d2", "d3", "l3", "l4", "d6", "d7", "d8", "d9"))
        self.wheel_attachment.set_pos(self.steer_attachment, d3 * self.x +
                                      (d2 + self.q[0]) * self.z)
        self.body.masscenter.set_pos(self.wheel_attachment, l3 * self.x +
                                     (l4 - self.q[0]) * self.z)
        self.left_hand_grip.set_pos(self.steer_attachment,
                                    d6 * self.x - d7 * self.y + d8 * self.z)
        self.right_hand_grip.set_pos(self.steer_attachment,
                                     d6 * self.x + d7 * self.y + d8 * self.z)
        self.suspension_stanchions.set_pos(self.steer_attachment, d9 * self.x)
        self.suspension_slider.set_pos(self.suspension_stanchions,
                                       self.q[0] * self.z)
        self.body.masscenter.set_vel(self.frame, 0)
        self.steer_attachment.set_vel(self.frame, 0)
        self.wheel_attachment.set_vel(self.frame, self.u[0] * self.z)
        self.left_hand_grip.set_vel(self.frame, 0)
        self.right_hand_grip.set_vel(self.frame, 0)
        self.suspension_stanchions.set_vel(self.frame, 0)
        self.suspension_slider.set_vel(self.frame, self.u[0] * self.z)
        self.system.add_coordinates(*self.q)
        self.system.add_speeds(*self.u)
        self.system.add_kdes(*(self.q.diff(dynamicsymbols._t) - self.u))

    def _define_loads(self) -> None:
        """Define the loads of the front frame."""
        super()._define_loads()
        force = -self.symbols["k"] * self.q[0] - self.symbols["c"] * self.u[0]
        self.system.add_loads(
            Force(self.suspension_stanchions, force * self.z),
            Force(self.suspension_slider, -force * self.z)
        )

    @property
    def steer_axis(self) -> Vector:
        """Steer axis expressed in the front frame."""
        return self.z

    @property
    def wheel_axis(self) -> Vector:
        """Wheel axis expressed in the front frame."""
        return self.y

    @property
    def steer_attachment(self) -> Point:
        """Attachment point between the rear frame and the front frame."""
        return self._steer_attachment

    @property
    def suspension_stanchions(self) -> Point:
        """Point representing the suspension stanchions, where the force is applied."""
        return self._suspension_stanchions

    @property
    def suspension_slider(self) -> Point:
        """Point representing the suspension slider, where the force is applied."""
        return self._suspension_slider

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get the parameter values of the front frame."""
        params = super().get_param_values(bicycle_parameters)
        str_params = _get_front_frame_moore_params(bicycle_parameters)
        if "mass" in str_params:
            params[self.body.mass] = str_params["mass"]
        if "inertia_vals" in str_params:
            params.update(get_inertia_vals(self.body, *str_params["inertia_vals"]))
        for name in ("d2", "d3", "l3", "l4", "d6", "d7", "d8"):
            if name in str_params:
                params[self.symbols[name]] = str_params[name]
        return params

    def set_plot_objects(self, plot_object: PlotModel) -> None:
        """Set the symmeplot plot objects."""
        super().set_plot_objects(plot_object)
        steer_top = self.steer_attachment.locatenew(
            "P", self.steer_axis * self.left_hand_grip.pos_from(
                self.steer_attachment).dot(self.steer_axis))
        plot_object.add_line([
            self.wheel_attachment, self.steer_attachment, steer_top,
            self.left_hand_grip, steer_top, self.right_hand_grip], self.name)


def _get_front_frame_moore_params(bicycle_parameters: Bicycle
                                  ) -> dict[str, float]:  # pragma: no cover
    params = {}
    if "Benchmark" in bicycle_parameters.parameters:
        bp = remove_uncertainties(bicycle_parameters.parameters["Benchmark"])
        mop = benchmark_to_moore(bp)
        params["mass"] = mop["me"]
        params["inertia_vals"] = (mop["ie11"], mop["ie22"], mop["ie33"], mop["ie12"],
                                  mop["ie23"], mop["ie31"])
        for name in ("d2", "d3", "l3", "l4"):
            params[name] = mop[name]
    if "Measured" in bicycle_parameters.parameters:
        mep = remove_uncertainties(bicycle_parameters.parameters["Measured"])
        rr, rf, w, lamht, whb, lhbr, lhbf = (mep.get(name) for name in (
            "rR", "rF", "w", "lamht", "whb", "LhbR", "LhbF"))
        if "Benchmark" in bicycle_parameters.parameters:
            rr = bp["rR"]
            rf = bp["rF"]
            w = bp["w"]
            lamht = np.pi / 2 - bp["lam"]
            d2, d3 = mop["d2"], mop["d3"]
        else:
            d2, d3 = None, None
        if whb is not None:
            params["d7"] = mep["whb"] / 2
        if not any(value is None for value in (rr, rf, w, lamht, whb, lhbr, lhbf,
                                               d2, d3)):
            def f(vals: tuple[float, ...]) -> tuple[float, ...]:
                ay, az, by, bz = vals
                return (
                    -lhbf + np.sqrt(ay ** 2 + az ** 2 + 0.25 * whb ** 2),
                    -lhbr + np.sqrt(by ** 2 + bz ** 2 + 0.25 * whb ** 2),
                    ay - by - w,
                    az - bz + rf - rr
                )

            ay, az, by, bz = fsolve(f, (0.3, 0.8, -0.7, 0.8))
            params["d6"] = -(ay * np.sin(lamht) - az * np.cos(lamht) - d3)
            params["d8"] = -(ay * np.cos(lamht) + az * np.sin(lamht) - d2)
    return params
