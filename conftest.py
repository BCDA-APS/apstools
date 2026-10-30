import pytest

################################################################################
# Add an option for default skipping tests that require the IOC's to be running
################################################################################
def pytest_addoption(parser):
    parser.addoption(
        "--skip-iocs", action="store_true", default=False, help="skip tests that require running EPICS IOCs"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "iocs: mark test as requiring IOCs")


def modify_skipiocs(config, items):
    if not config.getoption("--skip-iocs"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_iocs = pytest.mark.skip(reason="--skip-iocs option given")
    for item in items:
        if "iocs" in item.keywords:
            item.add_marker(skip_iocs)


def pytest_collection_modifyitems(config, items):
    modify_skipiocs(config, items)
