from .. import EpicsScanIdSignal
from ...tests import IOC
from ophyd import EpicsSignal
import bluesky
import bluesky.plans as bp
import pytest

SCAN_ID_PV = f"{IOC}gp:int1"


@pytest.mark.parametrize(
    "pvname, initial_value",
    [
        [None, 0],
        [SCAN_ID_PV, 0],
        [SCAN_ID_PV, 101],
    ],
)
def test_usage(pvname, initial_value):
    if pvname is None:
        scan_id_epics = None
        callback = None
    else:
        scan_id_epics = EpicsScanIdSignal(pvname, name="scan_id_epics")
        scan_id_epics.wait_for_connection()
        scan_id_epics.put(initial_value)
        callback = scan_id_epics.cb_scan_id_source

    if scan_id_epics is None:
        RE = bluesky.RunEngine({})
    else:
        RE = bluesky.RunEngine({}, scan_id_source=callback)
    assert isinstance(RE.md, dict)
    assert "scan_id" not in RE.md

    signal = EpicsSignal(f"{IOC}gp:float1", name="signal")
    signal.wait_for_connection()

    RE(bp.count([signal]))
    assert "scan_id" in RE.md
    assert RE.md["scan_id"] == initial_value + 1
