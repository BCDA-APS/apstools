import pytest

from ...tests import IOC_GP
from ...tests import timed_pause
from ..epid import EpidRecord
from ..epid import Fb_EpidDatabase
from ..epid import Fb_EpidDatabaseHeaterSimulator


@pytest.mark.parametrize(
    "support",
    [EpidRecord, Fb_EpidDatabase, Fb_EpidDatabaseHeaterSimulator],
)
def test_connection(support):
    """Connection test."""
    epid = support(f"{IOC_GP}epid1", name="epid")
    epid.wait_for_connection()
    assert epid.connected


@pytest.mark.parametrize(
    "method, scan, Kp, Ki",
    [
        ["reset", 0, 0, 0],
        ["setup", 8, 4e-4, 0.5],
    ],
)
def test_sim_heater(method, scan, Kp, Ki):
    epid = Fb_EpidDatabaseHeaterSimulator(f"{IOC_GP}epid1", name="epid")
    epid.wait_for_connection()

    getattr(epid, method)()
    timed_pause()
    assert epid.scanning_rate.get() == scan
    assert epid.proportional_gain.get() == Kp
    assert epid.integral_gain.get() == Ki
