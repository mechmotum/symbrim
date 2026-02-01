"""Pytest configuration for benchmarks with operation count display."""

from __future__ import annotations

import json
from pathlib import Path


def pytest_terminal_summary(terminalreporter):
    """Add operation count summary after benchmark results."""
    if not hasattr(terminalreporter.config, "_benchmarksession"):
        return

    bench_session = terminalreporter.config._benchmarksession
    if not bench_session.benchmarks:
        return

    # Display operation counts summary
    terminalreporter.write_line("")
    terminalreporter.write_line("Operation Counts:", bold=True, yellow=True)
    terminalreporter.write_line("-" * 80, yellow=True)

    # Group benchmarks
    groups = {}
    for bench in bench_session.benchmarks:
        if not bench or not hasattr(bench, "extra_info"):
            continue
        group = bench.group or "default"
        if group not in groups:
            groups[group] = []
        groups[group].append(bench)

    # Display by group
    for group_name, benchmarks in groups.items():
        if len(groups) > 1:
            terminalreporter.write_line(f"\n{group_name}:", bold=True)

        # Header
        terminalreporter.write_line(
            f"{'Name':<50} {'#Ops':>10} {'#Ops (CSE)':>12}"
        )
        terminalreporter.write_line("-" * 80)

        # Rows
        for bench in benchmarks:
            ops = bench.extra_info.get("operation_eoms", "N/A")
            ops_cse = bench.extra_info.get("operation_eoms_csed", "N/A")
            name = bench.name[:47] + "..." if len(bench.name) > 50 else bench.name
            terminalreporter.write_line(f"{name:<50} {ops:>10} {ops_cse:>12}")

    terminalreporter.write_line("")

    # Check for regression if baseline exists
    _check_regression(terminalreporter, bench_session)


def _check_regression(terminalreporter, bench_session):
    """Check for operation count regressions against baseline."""
    baseline_file = Path(".benchmarks/baseline.json")
    if not baseline_file.exists():
        return

    # Load baseline
    with baseline_file.open() as f:
        baseline_data = json.load(f)

    regressions = []
    for bench in bench_session.benchmarks:
        if not bench or not hasattr(bench, "extra_info"):
            continue

        fullname = bench.fullname
        current_ops = bench.extra_info.get("operation_eoms_csed")
        if current_ops is None:
            continue

        baseline_bench = baseline_data.get(fullname)
        if not baseline_bench:
            continue

        baseline_ops = baseline_bench.get("operation_eoms_csed")
        if baseline_ops is None:
            continue

        if current_ops > baseline_ops:
            increase = ((current_ops - baseline_ops) / baseline_ops) * 100
            regressions.append(
                (bench.name, baseline_ops, current_ops, increase)
            )

    if regressions:
        terminalreporter.write_line("")
        terminalreporter.write_line(
            "⚠️  Operation Count Regression Detected:",
            bold=True,
            red=True,
        )
        terminalreporter.write_line("-" * 80, yellow=True)
        for name, baseline, current, increase in regressions:
            terminalreporter.write_line(
                f"  {name}: {baseline} ops -> {current} ops (+{increase:.1f}%)",
                red=True,
            )
        terminalreporter.write_line("")
        raise AssertionError(
            "Benchmark regression: Operation counts increased. "
            "See details above."
        )
