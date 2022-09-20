import pytest

from ..iocstats import IocStatsDevice
from ...tests import common_attribute_quantities_test
from ...tests import IOC
from ...tests import short_delay_for_EPICS_IOC_database_processing


@pytest.mark.parametrize(
    "device, pv, connect, attr, expected",
    [
        [IocStatsDevice, IOC, False, "read_attrs", 19],
        [IocStatsDevice, IOC, False, "configuration_attrs", 8],
        [IocStatsDevice, IOC, True, "read()", 19],
        [IocStatsDevice, IOC, True, "summary()", 73],
    ]
)
def test_attribute_quantities(device, pv, connect, attr, expected):
    """Verify the quantities of the different attributes."""
    common_attribute_quantities_test(device, pv, connect, attr, expected)


@pytest.mark.parametrize(
    "attr, expected, comparison",
    [
        ["access", "Running", None],
        ["application_directory", "iocxxx", "end"],
        ["engineer", "engineer", None],
        ["epics_version", "EPICS", "start"],
        ["kernel_version", "Linux", "start"],
        ["kernel_version", "x86_64", "end"],
        ["location", "location", None],
        ["records_count", 100, ">="],
    ]
)
def test_running(attr, expected, comparison):
    gp_info = IocStatsDevice(IOC, name="gp_info")
    gp_info.wait_for_connection()
    assert gp_info.connected
    short_delay_for_EPICS_IOC_database_processing()

    assert hasattr(gp_info, attr)
    value = getattr(gp_info, attr).get(use_monitor=False)
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
