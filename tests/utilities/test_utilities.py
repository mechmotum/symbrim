from __future__ import annotations

import pytest
from brim.utilities.utilities import check_zero, random_eval
from sympy import S, acos, cos, sqrt, symbols
from sympy.abc import a, b, c
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


class TestCheckZero:
    @pytest.mark.parametrize("expr", [
        acos(cos(a)) - a + sqrt(b**2) - b + sqrt(c**2) - c,
        sqrt(dynamicsymbols("x", 1)**2) - dynamicsymbols("x", 1),
        S.Zero,
        ])
    @pytest.mark.parametrize("args, kwargs", [
        ((), {}),
        ((), {"n_evaluations": 100, "atol": 1e-10}),
    ])
    def test_is_zero(self, expr, args, kwargs) -> None:
        assert check_zero(expr, *args, **kwargs)

    @pytest.mark.parametrize("expr", [
        acos(cos(a)) - a + sqrt(b**2) - b + sqrt(c**2),
        sqrt(dynamicsymbols("x", 1)**2),
        ])
    @pytest.mark.parametrize("args, kwargs", [
        ((), {}),
        ((), {"n_evaluations": 100, "atol": 1e-10}),
    ])
    def test_is_not_zero(self, expr, args, kwargs) -> None:
        assert not check_zero(expr, *args, **kwargs)

    def test_too_loose_tolerance(self) -> None:
        assert check_zero(acos(cos(a)) - a + 0.001, atol=1e-2)
