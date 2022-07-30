# content of conftest.py

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--run-local", action="store_true", default=False, help="run local tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "local: mark test to run locally")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-local"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_local = pytest.mark.skip(reason="need --run-local option to run")
    for item in items:
        if "local" in item.keywords:
            item.add_marker(skip_local)
