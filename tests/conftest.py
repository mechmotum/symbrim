"""Pytest configuration for test collection and markers."""


def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow "
        "(skipped by default, run with '-m slow' or '--run-slow')",
    )


def pytest_addoption(parser):
    """Add command line options for slow tests."""
    parser.addoption(
        "--run-slow",
        action="store_true",
        default=False,
        help="Run slow tests (skipped by default)",
    )


def pytest_collection_modifyitems(config, items):
    """Skip slow tests by default unless --run-slow is specified."""
    if config.getoption("--run-slow"):
        # --run-slow given in cli: do not skip slow tests
        return

    skip_slow = config.getoption("-m", default="") != "slow"
    if skip_slow:
        import pytest
        skip_marker = pytest.mark.skip(reason="slow test (use --run-slow to run)")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_marker)
