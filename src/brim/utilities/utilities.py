"""Utilities for brim."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sympy import Basic, Derivative, Dummy, lambdify
from sympy.core.random import random
from sympy.physics.mechanics import find_dynamicsymbols, msubs

if TYPE_CHECKING:
    from sympy import Expr


__all__ = ["random_eval"]


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
