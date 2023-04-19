"""Module containing connections between the pelvis and the torso."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sympy import Symbol
from sympy.physics.mechanics import WeldJoint
from sympy.physics.mechanics._system import System

from brim.rider.base_connections import PelvisToTorsoBase

if TYPE_CHECKING:
    from sympy.physics.mechanics import Vector

__all__ = ["FixedPelvisToTorso"]


class FixedPelvisToTorso(PelvisToTorsoBase):
    """Connection between the pelvis and the torso with a fixed connection."""

    @property
    def descriptions(self) -> dict[Any, str]:
        """Return the descriptions."""
        return {
            **super().descriptions,
            self.symbols["d"]: "Distance from the torso center of mass to the pelvis.",
        }

    def define_objects(self) -> None:
        """Define the objects."""
        super().define_objects()
        self.symbols["d"] = Symbol(self._add_prefix("d"))
        self._torso_wrt_pelvis = -self.symbols["d"] * self.pelvis.z
        self._system = System.from_newtonian(self.pelvis.body)

    def define_kinematics(self) -> None:
        """Define the kinematics."""
        super().define_kinematics()
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
