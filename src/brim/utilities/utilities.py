"""Utilities for brim."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sympy import Basic, Derivative, Dummy, ImmutableMatrix, lambdify, zeros
from sympy.core.cache import cacheit
from sympy.core.random import random
from sympy.physics.mechanics import find_dynamicsymbols, msubs

if TYPE_CHECKING:
    from sympy import Expr


__all__ = ["cramer_solve"]


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


def random_eval(expr: Expr, prec: int = 7, method: str = "lambdify") -> float:
    """Evaluate an expression with random values."""
    if not isinstance(expr, Basic):
        return expr
    free = tuple(expr.free_symbols.union(find_dynamicsymbols(expr)))
    if method == "lambdify":
        if any(isinstance(f, Derivative) for f in free):
            dummy_map = {f: Dummy() for f in free if isinstance(f, Derivative)}
            free = tuple(dummy_map.get(f, f) for f in free)
            expr = msubs(expr, dummy_map)
        return round(lambdify(free, expr, cse=True)(*(random() for _ in free)), prec)
    elif method == "evalf":
        return round(expr.evalf(prec, {s: random() for s in free}), prec)
    else:
        raise NotImplementedError(f"Method {method} not implemented.")
