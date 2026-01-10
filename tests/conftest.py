"""Pytest configuration for test collection and markers."""


def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow "
        "(skipped by default, run with '-m slow' or '--run-all')",
    )


def pytest_addoption(parser):
    """Add command line options for slow tests."""
    parser.addoption(
        "--run-all",
        action="store_true",
        default=False,
        help="Run all tests including slow tests",
    )


def pytest_collection_modifyitems(config, items):
    """Skip slow tests by default unless --run-all is specified."""
    if config.getoption("--run-all"):
        # --run-all given in cli: do not skip slow tests
        return

    skip_slow = config.getoption("-m", default="") != "slow"
    if skip_slow:
        import pytest
        skip_marker = pytest.mark.skip(reason="slow test (use --run-all to run)")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_marker)
