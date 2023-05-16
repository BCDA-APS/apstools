import pytest

from ...tests import IOC
from ..epid import EpidRecord
from ..epid import Fb_EpidDatabase
from ..epid import Fb_EpidDatabaseHeaterSimulator


@pytest.mark.parametrize(
    "support", [EpidRecord, Fb_EpidDatabase, Fb_EpidDatabaseHeaterSimulator],
)
def test_connection(support):
    """Connection test."""
    epid = support(f"{IOC}epid1", name="epid")
    epid.wait_for_connection()
    assert epid.connected


@pytest.mark.parametrize(
    "method, scan, Kp, Ki, hi",
    [
        ["reset", 0, 0, 0, 1.0],
        ["setup", 8, 4e-4, 0.5, 1.0],
    ],
)
def test_sim_heater(method, scan, Kp, Ki, hi):
    epid = Fb_EpidDatabaseHeaterSimulator(f"{IOC}epid1", name="epid")
    epid.wait_for_connection()

    getattr(epid, method)()
    assert epid.scanning_rate.get() == scan
    assert epid.proportional_gain.get() == Kp
    assert epid.integral_gain.get() == Ki
    assert epid.high_limit.get() == hi
