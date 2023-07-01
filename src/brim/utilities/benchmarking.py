"""Module containing utilities to easily benchmark models."""

from typing import Optional

import pytest
from sympy import count_ops, cse
from sympy.core.cache import clear_cache

__all__ = ["benchmark"]


def benchmark(rounds: int = 3, group: Optional[str] = None):
    """Create decorator to benchmark a function.

    Parameters
    ----------
    rounds : int, optional
        Number of rounds to run the benchmark for, by default 3.
    group : Optional[str], optional
        Group to put the benchmark in, by default None.

    Returns
    -------
    function
        Decorated function.

    """

    def decorator(func):
        @pytest.mark.benchmark(group=group)
        def wrapper(benchmark):
            data = {}

            def setup():
                clear_cache()
                data["system"] = func()

            def form_eoms():
                data["eoms"] = data["system"]._form_eoms()

            benchmark.pedantic(form_eoms, setup=setup, rounds=rounds)
            benchmark.extra_info["operation_eoms"] = count_ops(data["eoms"])
            benchmark.extra_info["operation_eoms_csed"] = count_ops(cse(data["eoms"]))

        return wrapper

    return decorator
