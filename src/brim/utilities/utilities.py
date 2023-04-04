"""Utilities for brim."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sympy import ImmutableMatrix, zeros
from sympy.core.cache import cacheit
from sympy.physics.mechanics import System

if TYPE_CHECKING:
    from brim.core import ModelBase

__all__ = ["merge_systems", "to_system", "cramer_solve"]


def to_system(model: ModelBase) -> System:  # pragma: no cover
    """Export the Whipple bicycle to a Sympy system."""

    def get_systems(model):
        """Get the systems of the submodels."""
        return ([model.system] +
                [s for submodel in model.submodels for s in get_systems(submodel)])

    return merge_systems(model.system, *get_systems(model))


def merge_systems(*systems: System) -> System:  # pragma: no cover
    """Combine multiple system instance into one."""
    system = System(systems[0].origin, systems[0].frame)
    for s in systems:
        for qi in s.q_ind:
            if qi not in system.q:
                system.add_coordinates(qi, independent=True)
        for qi in s.q_dep:
            if qi not in system.q:
                system.add_coordinates(qi, independent=False)
        for ui in s.u_ind:
            if ui not in system.u:
                system.add_speeds(ui, independent=True)
        for ui in s.u_dep:
            if ui not in system.u:
                system.add_speeds(ui, independent=False)
        for body in s.bodies:
            if body not in system.bodies:
                system.add_bodies(body)
        for joint in s.joints:
            if joint not in system.joints:
                system.add_joints(joint)
        for load in s.loads:
            if load not in system.loads:
                system.add_loads(load)
        for kde in s.kdes:
            if kde not in system.kdes:
                system.add_kdes(kde)
        for fh in s.holonomic_constraints:
            if fh not in system.holonomic_constraints:
                system.add_holonomic_constraints(fh)
        for fnh in s.nonholonomic_constraints:
            if fnh not in system.nonholonomic_constraints:
                system.add_nonholonomic_constraints(fnh)
    return system


@cacheit
def det_laplace(matrix):  # pragma: no cover
    """Compute the determinant of a matrix using Laplace's formula."""
    n = matrix.shape[0]
    if n == 1:
        return matrix[0]
    elif n == 2:
        return matrix[0, 0] * matrix[1, 1] - matrix[0, 1] * matrix[1, 0]
    else:
        return sum((-1) ** i * matrix[0, i] *
                   det_laplace(matrix.minor_submatrix(0, i)) for i in range(n))


def cramer_solve(mat, rhs, det_method=det_laplace):  # pragma: no cover
    """Solve a system of linear equations using Cramer's rule."""

    def entry(i, j):
        return rhs[i, sol] if j == col else mat[i, j]

    mat_im = ImmutableMatrix(mat)  # Convert to immutable for cache purposes
    det_mat = det_method(mat_im)
    x = zeros(*rhs.shape)
    for sol in range(rhs.shape[1]):
        for col in range(rhs.shape[0]):
            x[col, sol] = det_method(ImmutableMatrix(*mat_im.shape, entry)) / det_mat
    return x
