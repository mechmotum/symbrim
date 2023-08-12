"""Module containing the Whipple bicycle model."""
from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING, Any

from sympy import Matrix, Symbol
from sympy.physics.mechanics import PinJoint, ReferenceFrame, Vector, dynamicsymbols
from sympy.physics.mechanics._system import System

from brim.bicycle.bicycle_base import BicycleBase
from brim.bicycle.front_frames import FrontFrameBase
from brim.bicycle.grounds import GroundBase
from brim.bicycle.rear_frames import RearFrameBase
from brim.bicycle.tyre_models import TyreBase
from brim.bicycle.wheels import WheelBase
from brim.core import ConnectionRequirement, ModelRequirement, set_default_convention

try:  # pragma: no cover
    import numpy as np
    from bicycleparameters.io import remove_uncertainties

    if TYPE_CHECKING:
        from bicycleparameters import Bicycle
except ImportError:  # pragma: no cover
    pass

__all__ = ["WhippleBicycle", "WhippleBicycleMoore"]


@set_default_convention("moore")
class WhippleBicycle(BicycleBase):
    """Base class for the Whipple bicycle model."""

    required_models: tuple[ModelRequirement, ...] = (
        ModelRequirement("ground", GroundBase, "Submodel of the ground."),
        ModelRequirement("rear_frame", RearFrameBase, "Submodel of the rear frame."),
        ModelRequirement("front_frame", FrontFrameBase, "Submodel of the front frame."),
        ModelRequirement("rear_wheel", WheelBase, "Submodel of the rear wheel."),
        ModelRequirement("front_wheel", WheelBase, "Submodel of the front wheel."),
    )
    required_connections: tuple[ConnectionRequirement, ...] = (
        ConnectionRequirement("front_tyre", TyreBase,
                              "Tyre model for the front wheel."),
        ConnectionRequirement("rear_tyre", TyreBase,
                              "Tyre model for the rear wheel."),
    )
    ground: GroundBase
    rear_frame: RearFrameBase
    front_frame: FrontFrameBase
    rear_wheel: WheelBase
    front_wheel: WheelBase
    rear_tyre: TyreBase
    front_tyre: TyreBase

    def _define_connections(self) -> None:
        """Define the connections between the submodels."""
        super()._define_connections()
        self.rear_tyre.ground = self.ground
        self.rear_tyre.wheel = self.rear_wheel
        self.front_tyre.ground = self.ground
        self.front_tyre.wheel = self.front_wheel


class WhippleBicycleMoore(WhippleBicycle):
    """Whipple bicycle model based on Moore's convention."""

    convention: str = "moore"

    @property
    def descriptions(self) -> dict[Any, str]:
        """Dictionary of descriptions of the Whipple bicycle's attributes."""
        desc = {
            **super().descriptions,
            self.q[0]: f"Perpendicular distance along ground.x to the rear contact "
                       f"point in the ground plane of {self.name}.",
            self.q[1]: f"Perpendicular distance along ground.y to the rear contact "
                       f"point in the ground plane of {self.name}.",
            self.q[2]: f"Yaw angle of the rear frame of {self.name}.",
            self.q[3]: f"Roll angle of the rear frame of {self.name}.",
            self.q[4]: f"Pitch angle of the rear frame of {self.name}.",
            self.q[5]: f"Front wheel rotation angle of {self.name}.",
            self.q[6]: f"Steering rotation angle of {self.name}.",
            self.q[7]: f"Rear wheel rotation angle of {self.name}.",
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
        self._system = System(self.ground.system.origin, self.ground.frame)
        self.rear_tyre.define_objects()
        self.rear_tyre.on_ground = True
        self.front_tyre.define_objects()
        self.q = Matrix(dynamicsymbols(self._add_prefix("q1:9")))
        self.u = Matrix(dynamicsymbols(self._add_prefix("u1:9")))
        self.symbols.update({name: Symbol(
            self._add_prefix(name)) for name in ("gear_ratio", "l_px", "l_pz")})

    def _define_kinematics(self) -> None:
        """Define the kinematics of the Whipple bicycle."""
        super()._define_kinematics()
        qd_repl = dict(zip(self.q.diff(dynamicsymbols._t), self.u))
        # Define the location of the rear wheel contact point in the ground frame.
        self.ground.set_pos_point(self.rear_tyre.contact_point, self.q[:2])
        self.rear_tyre.contact_point.set_vel(
            self.ground.frame,
            self.rear_tyre.contact_point.vel(self.ground.frame).xreplace(qd_repl))
        # Define the orientation of the rear frame.
        int_frame = ReferenceFrame("int_frame")
        int_frame.orient_body_fixed(self.ground.frame, (*self.q[2:4], 0), "zxy")
        self.rear_frame.frame.orient_axis(int_frame, int_frame.y, self.q[4])
        self.rear_frame.frame.set_ang_vel(
            self.ground.frame,
            self.rear_frame.frame.ang_vel_in(self.ground.frame).xreplace(qd_repl))
        # Define the joints
        self.system.add_joints(
            PinJoint(self._add_prefix("rear_wheel_joint"), self.rear_frame.body,
                     self.rear_wheel.body, self.q[5], self.u[5],
                     self.rear_frame.wheel_attachment, self.rear_wheel.center,
                     self.rear_frame.wheel_axis, self.rear_wheel.rotation_axis),
            PinJoint(self._add_prefix("steer_joint"), self.rear_frame.body,
                     self.front_frame.body, self.q[6], self.u[6],
                     self.rear_frame.steer_attachment,
                     self.front_frame.steer_attachment, self.rear_frame.steer_axis,
                     self.front_frame.steer_axis),
            PinJoint(self._add_prefix("front_wheel_joint"), self.front_frame.body,
                     self.front_wheel.body, self.q[7], self.u[7],
                     self.front_frame.wheel_attachment, self.front_wheel.center,
                     self.front_frame.wheel_axis, self.front_wheel.rotation_axis),
        )
        # Define contact points.
        with contextlib.suppress(ValueError):
            self.rear_tyre.upward_radial_axis = Vector(
                {int_frame: self.ground.get_normal(
                    self.rear_tyre.contact_point).to_matrix(self.ground.frame)})
        self.rear_tyre.define_kinematics()
        self.front_tyre.define_kinematics()
        # Add the coordinates and speeds to the system.
        self.system.add_coordinates(*self.q[:5])
        self.system.add_speeds(*self.u[:5])
        self.system.add_kdes(*(
            ui - qi.diff(dynamicsymbols._t) for qi, ui in zip(self.q[:5], self.u[:5])))
        if self.pedals:
            self.pedals.center_point.set_pos(self.rear_wheel.center,
                                             self.symbols["l_px"] * self.rear_frame.x +
                                             self.symbols["l_pz"] * self.rear_frame.z)
            self.pedals.frame.orient_axis(
                self.rear_frame.frame, self.rear_frame.wheel_axis,
                self.q[7] / self.symbols["gear_ratio"])
            self.pedals.frame.set_ang_vel(
                self.rear_frame.frame,
                self.u[7] / self.symbols["gear_ratio"] * self.rear_frame.wheel_axis)

    def _define_loads(self) -> None:
        """Define the loads of the Whipple bicycle."""
        super()._define_loads()
        self.rear_tyre.define_loads()
        self.front_tyre.define_loads()

    def _define_constraints(self) -> None:
        """Define the constraints of the Whipple bicycle."""
        super()._define_constraints()
        self.rear_tyre.define_constraints()
        self.front_tyre.define_constraints()

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
