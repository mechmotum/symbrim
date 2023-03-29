"""BRiM.

A Modular and Extensible Open-Source Framework for Creating Bicycle-Rider Models.
"""
__all__ = [
    "WhippleBicycle", "FlatGround", "RigidRearFrame", "RigidFrontFrame",
    "KnifeEdgeWheel", "NonHolonomicTyreModel",
]

from brim.bicycle import (
    FlatGround,
    KnifeEdgeWheel,
    NonHolonomicTyreModel,
    RigidFrontFrame,
    RigidRearFrame,
    WhippleBicycle,
)
