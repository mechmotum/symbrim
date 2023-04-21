from __future__ import annotations

import pytest
from brim.utilities.utilities import random_eval
from sympy import sqrt, symbols
from sympy.physics.mechanics import dynamicsymbols


class TestRandomEval:
    @pytest.mark.parametrize("method", ["lambdify", "evalf"])
    @pytest.mark.parametrize("expr", [
        dynamicsymbols("x"),
        sum(symbols("a:z")),
        dynamicsymbols("x").diff()
    ])
    def test_non_zero(self, expr, method) -> None:
        assert random_eval(expr, method=method) != 0

    @pytest.mark.parametrize("method", ["lambdify", "evalf"])
    @pytest.mark.parametrize("expr", [
        sqrt(dynamicsymbols("x") ** 2) - dynamicsymbols("x"),
    ])
    def test_zero(self, expr, method) -> None:
        assert random_eval(expr, method=method) == 0

    @pytest.mark.parametrize("method", ["lambdify", "evalf"])
    @pytest.mark.parametrize("expr", [3, 3.3])
    def test_non_expression(self, expr, method) -> None:
        assert random_eval(expr, method=method) == expr

    def test_not_implemented(self) -> None:
        with pytest.raises(NotImplementedError):
            random_eval(symbols("a"), method="not_implemented")
