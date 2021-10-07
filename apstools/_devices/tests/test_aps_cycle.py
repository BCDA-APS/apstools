"""
test the APS cycle computation code
"""

import dm
import socket

from .. import ApsCycleComputedRO
from .. import ApsCycleDM


def using_APS_workstation():
    hostname = socket.gethostname()
    return hostname.lower().endswith(".aps.anl.gov")


def test_ApsCycleComputedRO():
    signal = ApsCycleComputedRO(name="signal")
    assert signal.connected

    cycle = signal.get()  # expect 2021-3 or such
    assert isinstance(cycle, str)
    assert cycle != ""
    assert len(cycle) == 6
    assert cycle.startswith("20")
    assert cycle.find("-") >= 0


def test_ApsCycleDM():
    if not using_APS_workstation():
        assert True
        return

    # test requires APS subnet
    signal = ApsCycleDM(name="signal")
    assert signal.connected

    cycle = signal.get()  # expect 2021-3 or such
    assert isinstance(cycle, str)
    assert cycle != ""
    assert len(cycle) == 6
    assert cycle.startswith("20")
    assert cycle.find("-") >= 0
