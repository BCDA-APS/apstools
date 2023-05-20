import time

import pytest

from ...tests import IOC_GP
from ...tests import common_attribute_quantities_test
from ...tests import timed_pause
from ..iocstats import IocStatsDevice


@pytest.mark.parametrize(
    "device, pv, connect, attr, expected",
    [
        [IocStatsDevice, IOC_GP, False, "read_attrs", 19],
        [IocStatsDevice, IOC_GP, False, "configuration_attrs", 8],
        [IocStatsDevice, IOC_GP, True, "read()", 19],
        [IocStatsDevice, IOC_GP, True, "summary()", 73],
    ],
)
def test_attribute_quantities(device, pv, connect, attr, expected):
    """Verify the quantities of the different attributes."""
    common_attribute_quantities_test(device, pv, connect, attr, expected)


@pytest.mark.parametrize(
    "attr, expected, comparison",
    [
        ["access", "Running", None],
        # TODO: ["application_directory", "iocxxx", "end"],
        ["engineer", "engineer", None],
        ["epics_version", "EPICS", "start"],
        ["kernel_version", "Linux", "start"],
        ["kernel_version", "x86_64", "end"],
        ["location", "location", None],
        ["records_count", 100, ">="],
    ],
)
def test_running(attr, expected, comparison):
    gp_info = IocStatsDevice(IOC_GP, name="gp_info")
    gp_info.wait_for_connection()
    assert gp_info.connected
    timed_pause()

    assert hasattr(gp_info, attr)
    value = getattr(gp_info, attr).get(use_monitor=False)
    time.sleep(0.1)
    if comparison == "start":
        assert value.startswith(expected)
    elif comparison == "end":
        assert value.endswith(expected)
    elif comparison == "find":
        assert value.find(expected) >= 0
    elif comparison == ">=":
        assert value >= 0
    else:
        assert value == expected
