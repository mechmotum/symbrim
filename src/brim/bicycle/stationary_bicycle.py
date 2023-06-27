"""Module containing the Whipple bicycle model."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sympy import Matrix, Symbol
from sympy.physics.mechanics import PinJoint, dynamicsymbols
from sympy.physics.mechanics._system import System

from brim.bicycle.bicycle_base import BicycleBase

try:  # pragma: no cover
    import numpy as np
    from bicycleparameters.io import remove_uncertainties

    if TYPE_CHECKING:
        from bicycleparameters import Bicycle
except ImportError:  # pragma: no cover
    pass

__all__ = ["StationaryBicycle"]


class StationaryBicycle(BicycleBase):
    """Stationary bicycle model."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Dictionary of descriptions of the Whipple bicycle's attributes."""
        desc = {
            **super().descriptions,
            self.q[0]: f"Front wheel rotation angle of {self.name}.",
            self.q[1]: f"Steering rotation angle of {self.name}.",
            self.q[2]: f"Rear wheel rotation angle of {self.name}.",
            self.symbols["gear_ratio"]: "Ratio between the angle of the rear wheel and"
                                        " the pedals.",
            self.symbols["l_px"]: f"Distance between the rear wheel and the pedals "
                                  f"along {self.rear_frame.x}.",
            self.symbols["l_pz"]: f"Distance between the rear wheel and the pedals "
                                  f"along {self.rear_frame.z}.",
        }
        desc.update({ui: f"Generalized speed of the {desc[qi].lower()}"
                     for qi, ui in zip(self.q, self.u)})
        return desc

    def _define_objects(self) -> None:
        """Define the objects of the Whipple bicycle."""
        super()._define_objects()
        self.q: Matrix = Matrix(dynamicsymbols(self._add_prefix("q1:4")))
        self.u: Matrix = Matrix(dynamicsymbols(self._add_prefix("u1:4")))
        self.symbols.update({name: Symbol(
            self._add_prefix(name)) for name in ("gear_ratio", "l_px", "l_pz")})
        self._system = System.from_newtonian(self.rear_frame.body)

    def _define_kinematics(self) -> None:
        """Define the kinematics of the Whipple bicycle."""
        super()._define_kinematics()
        # Define the joints
        if self.front_frame:
            self.system.add_joints(
                PinJoint(self._add_prefix("steer_joint"), self.rear_frame.body,
                         self.front_frame.body, self.q[1], self.u[1],
                         self.rear_frame.steer_attachment,
                         self.front_frame.steer_attachment, self.rear_frame.steer_axis,
                         self.front_frame.steer_axis)

            )
        if self.rear_wheel:
            self.system.add_joints(
                PinJoint(self._add_prefix("rear_wheel_joint"), self.rear_frame.body,
                         self.rear_wheel.body, self.q[2], self.u[2],
                         self.rear_frame.wheel_attachment, self.rear_wheel.center,
                         self.rear_frame.wheel_axis, self.rear_wheel.rotation_axis)
            )
        if self.front_wheel:
            self.system.add_joints(
                PinJoint(self._add_prefix("front_wheel_joint"), self.front_frame.body,
                         self.front_wheel.body, self.q[0], self.u[0],
                         self.front_frame.wheel_attachment, self.front_wheel.center,
                         self.front_frame.wheel_axis, self.front_wheel.rotation_axis),
            )
        if self.pedals:
            self.pedals.center_point.set_pos(self.rear_wheel.center,
                                             self.symbols["l_px"] * self.rear_frame.x +
                                             self.symbols["l_pz"] * self.rear_frame.z)
            self.pedals.frame.orient_axis(
                self.rear_frame.frame, self.rear_frame.wheel_axis,
                self.q[2] / self.symbols["gear_ratio"])
            self.pedals.frame.set_ang_vel(
                self.rear_frame.frame,
                self.u[2] / self.symbols["gear_ratio"] * self.rear_frame.wheel_axis)

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
                params[self.symbols["l_px"]] = (
                        glob_x * np.sin(lamht) - glob_z * np.cos(lamht))
                params[self.symbols["l_pz"]] = (
                        glob_x * np.cos(lamht) + glob_z * np.sin(lamht))
        return params
