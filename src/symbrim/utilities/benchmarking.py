"""Module containing utilities to easily benchmark models."""
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sympy import count_ops, cse
from sympy.core.cache import clear_cache

if TYPE_CHECKING:
    from collections.abc import Callable

    from pytest_benchmark.fixture import BenchmarkFixture
    from sympy.physics.mechanics import KanesMethod, System

__all__ = ["benchmark"]


def benchmark(
    rounds: int = 3, group: str | None = None, **kwargs: dict[str, object]
) -> Callable[[Callable[[], KanesMethod | System]], Callable]:
    """Create decorator to benchmark a function.

    Parameters
    ----------
    rounds : int, optional
        Number of rounds to run the benchmark for, by default 3.
    group : Optional[str], optional
        Group to put the benchmark in, by default None.
    kwargs
        If kwargs are provided, then they are passed to
        :meth:`sympy.physics.mechanics.system.System.form_eoms`.

    Returns
    -------
    function
        Decorated function, which should return an instance of
        :class:`sympy.physics.mechanics.system.System` or
        :class:`sympy.physics.mechanics.kane.KanesMethod`.

    """

    def decorator(func: Callable[[], KanesMethod | System]) -> Callable:
        @pytest.mark.benchmark(group=group)
        def wrapper(benchmark: BenchmarkFixture) -> None:
            data = {}

            def setup() -> None:
                clear_cache()

            def form_eoms() -> None:
                data["system"] = func()
                if hasattr(data["system"], "form_eoms"):
                    data["eoms"] = data["system"].form_eoms(**kwargs)
                else:
                    data["eoms"] = data["system"]._form_eoms()

            benchmark.pedantic(form_eoms, setup=setup, rounds=rounds)
            benchmark.extra_info["operation_eoms"] = count_ops(data["eoms"])
            benchmark.extra_info["operation_eoms_csed"] = count_ops(cse(data["eoms"]))

        return wrapper

    return decorator
