"""Module containing connections between the pelvis and the torso."""
from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from sympy import Symbol
from sympy.physics.mechanics import System, Vector, WeldJoint

from brim.rider.base_connections import SacrumBase

with contextlib.suppress(ImportError):
    import numpy as np

    if TYPE_CHECKING:
        from bicycleparameters import Bicycle

__all__ = ["FixedSacrum"]


class FixedSacrum(SacrumBase):
    """Connection to fixate the torso to the pelvis."""

    @property
    def descriptions(self) -> dict[object, str]:
        """Return the descriptions."""
        return {
            **super().descriptions,
            self.symbols["d_p_t"]: "Distance from the torso center of mass to the "
                                   "pelvis.",
        }

    def _define_objects(self) -> None:
        """Define the objects."""
        super()._define_objects()
        self.symbols["d_p_t"] = Symbol(self._add_prefix("d_p_t"))
        self._torso_wrt_pelvis = -self.symbols["d_p_t"] * self.pelvis.z
        self._system = System.from_newtonian(self.pelvis.body)

    def _define_kinematics(self) -> None:
        """Define the kinematics."""
        super()._define_kinematics()
        self.system.add_joints(
            WeldJoint(
                self._add_prefix("joint"), self.pelvis.body, self.torso.body,
                parent_point=self.torso_wrt_pelvis)
        )

    @property
    def torso_wrt_pelvis(self) -> Vector:
        """Return the position of the torso w.r.t. the pelvis center of mass."""
        return self._torso_wrt_pelvis

    @torso_wrt_pelvis.setter
    def torso_wrt_pelvis(self, value: Vector) -> None:
        try:
            value.express(self.pelvis.frame)
        except ValueError as e:
            raise ValueError(
                "Torso position must be expressable in the pelvis frame.") from e
        self._torso_wrt_pelvis = value

    def get_param_values(self, bicycle_parameters: Bicycle) -> dict[Symbol, float]:
        """Get a parameters mapping of a model based on a bicycle parameters object."""
        params = super().get_param_values(bicycle_parameters)
        human = bicycle_parameters.human
        if human is None:
            return params
        torso_props = human.combine_inertia(("T", "C"))
        params[self.symbols["d_p_t"]] = np.linalg.norm(
            torso_props[1] - human.P.center_of_mass)
        return params
