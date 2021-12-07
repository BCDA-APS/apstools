import pytest

from ..iocstats import IocStatsDevice


IOC = "gp:"


def test_read():
    gp_info = IocStatsDevice(IOC, name="gp_info")
    gp_info.wait_for_connection()
    assert gp_info.connected

    assert len(gp_info.read_attrs) == 19
    assert len(gp_info.configuration_attrs) == 8
    assert len(gp_info._summary().splitlines()) == 73


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

    assert hasattr(gp_info, attr)
    value = getattr(gp_info, attr).get()
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

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
