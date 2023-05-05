"""
test the APS cycle computation code
"""

import datetime
import socket

import pytest

from .. import ApsCycleDM
from .. import aps_cycle


def using_APS_workstation():
    hostname = socket.gethostname()
    return hostname.lower().endswith(".aps.anl.gov")


def test_ApsCycleDM():
    signal = ApsCycleDM(name="signal")
    assert signal.connected

    cycle = signal.get()  # expect 2021-3 or such
    assert isinstance(cycle, str)
    assert cycle != ""
    assert len(cycle) in (5, 6)  # 5 for APS-U
    assert cycle.find("-") >= 0
    if cycle.startswith("A"):
        assert cycle == "APS-U"
    else:
        assert cycle.startswith("20")
        assert int(cycle.split("-")[0]) > 2020


def test_ApsCycleDB():
    assert aps_cycle.YAML_CYCLE_FILE.exists()

    cycle = aps_cycle.cycle_db.get_cycle_name()
    assert cycle in aps_cycle.cycle_db.db
    assert isinstance(cycle, str)
    assert cycle != ""
    assert len(cycle) in (5, 6)  # 5 for APS-U
    assert cycle.find("-") >= 0
    if cycle.startswith("A"):
        assert cycle == "APS-U"
    else:
        assert cycle.startswith("20")
        assert int(cycle.split("-")[0]) > 2020


@pytest.mark.parametrize(
    "iso8601, cycle_name",
    [
        ["2014-06-28 01:23:45", "2014-2"],
        ["2021-09-28 12:34:56", "2021-2"],
        ["2021-09-30 23:59:59", "2021-2"],
        ["2021-10-02 00:00:00", "2021-3"],
        ["2023-10-02 00:00:00", "APS-U"],
        ["1999-06-01", None],
    ],
)
def test_cycles(iso8601, cycle_name):
    assert isinstance(iso8601, str)

    dt = datetime.datetime.fromisoformat(iso8601)
    ts = datetime.datetime.timestamp(dt)
    assert aps_cycle.cycle_db.get_cycle_name(ts) == cycle_name
