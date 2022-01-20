from ophyd import EpicsSignal

from ..positioner_soft_done import PVPositionerSoftDone
from ..positioner_soft_done import PVPositionerSoftDoneWithStop
from ...utils import run_in_thread

import pytest
import time

IOC = "gp:"
PV_PREFIX = f"{IOC}gp:"
SHORT_DELAY_FOR_EPICS = 0.02


@pytest.fixture(scope="function")
def rbv():
    "Writable readback value for tests."
    rbv = EpicsSignal(f"{PV_PREFIX}float1", name="rbv")
    rbv.wait_for_connection()
    yield rbv


@pytest.fixture(scope="function")
def prec():
    "PV precision."
    prec = EpicsSignal(f"{PV_PREFIX}float1.PREC", name="prec")
    prec.wait_for_connection()
    yield prec


@run_in_thread
def delayed_complete(pos, readback, delay=1):
    "Time-delayed completion of positioner move."
    time.sleep(delay)
    readback.put(pos.setpoint.get())


@run_in_thread
def delayed_stop(pos, delay=1):
    "Time-delayed stop of `pos`."
    time.sleep(delay)
    pos.stop()


def test_same_sp_and_rb():
    with pytest.raises(ValueError) as exc:
        PVPositionerSoftDone("", readback_pv="test", setpoint_pv="test", name="pos")
    assert str(exc.value).endswith("must have different values")


@pytest.mark.parametrize(
    "device, has_inposition",
    [
        [PVPositionerSoftDone, False],
        [PVPositionerSoftDoneWithStop, True]
    ]
)
def test_structure(device, has_inposition):
    "actual PVs not necessary for this test"
    pos = device("", readback_pv="r", setpoint_pv="v", name="pos")
    assert isinstance(pos, device)
    assert hasattr(pos, "inposition") is has_inposition
    assert pos.precision is None
    assert pos.prefix == ""
    assert pos.readback.pvname == "r"
    assert pos.report_dmov_changes.get() is False
    assert pos.setpoint.pvname == "v"
    assert pos.done.get() is True
    assert pos.done_value is True
    assert pos.target.get() == "None"
    assert pos.tolerance.get() == -1


def test_put_and_stop(rbv, prec):
    device = PVPositionerSoftDoneWithStop

    # the positioner to test
    pos = device(PV_PREFIX, readback_pv="float1", setpoint_pv="float2", name="pos")
    pos.wait_for_connection()
    assert pos.tolerance.get() == -1
    assert pos.precision == prec.get()

    # ensure starting value at 0.0
    pos.setpoint.put(0)
    rbv.put(1)  # make the readback to different
    time.sleep(SHORT_DELAY_FOR_EPICS)
    assert not pos.inposition

    rbv.put(0)  # make the readback match
    time.sleep(SHORT_DELAY_FOR_EPICS)
    assert pos.position == 0.0

    assert pos.done.get() is True
    assert pos.done_value is True
    assert pos.inposition

    # change the setpoint
    pos.setpoint.put(1)
    time.sleep(SHORT_DELAY_FOR_EPICS)
    assert not pos.inposition

    # change the readback to match
    rbv.put(1)
    time.sleep(SHORT_DELAY_FOR_EPICS)
    assert pos.inposition

    # change the setpoint
    pos.setpoint.put(0)
    time.sleep(SHORT_DELAY_FOR_EPICS)
    assert not pos.inposition

    # move the readback part-way, but move is not over yet
    rbv.put(0.5)
    time.sleep(SHORT_DELAY_FOR_EPICS)
    assert not pos.inposition

    # force a stop now
    pos.stop()
    time.sleep(SHORT_DELAY_FOR_EPICS)
    pos.cb_readback()
    time.sleep(SHORT_DELAY_FOR_EPICS)
    assert pos.setpoint.get() == 0.5
    assert pos.readback.get() == 0.5
    assert pos.position == 0.5
    assert pos.inposition


def test_move_and_stop(rbv):
    device = PVPositionerSoftDoneWithStop

    # the positioner to test
    pos = device(PV_PREFIX, readback_pv="float1", setpoint_pv="float2", name="pos")
    pos.wait_for_connection()

    # move to non-zero
    longer_delay = 5*SHORT_DELAY_FOR_EPICS
    delayed_complete(pos, rbv, delay=longer_delay)
    # t0 = time.time()  # time it
    target = 5.43
    pos.move(target)  # readback set by delayed_complete()
    # dt = time.time() - t0
    time.sleep(SHORT_DELAY_FOR_EPICS)
    # assert dt >= longer_delay
    assert pos.inposition

    # move that is stopped before reaching the target
    # t0 = time.time()  # time it
    delayed_stop(pos, longer_delay)
    assert pos.inposition

    pos.move(target - 1)  # readback set by delayed_stop()
    # dt = time.time() - t0
    # assert dt >= longer_delay
    time.sleep(SHORT_DELAY_FOR_EPICS)
    assert pos.setpoint.get() == target
    assert pos.position == target
    assert pos.inposition

    # move to 0.0
    delayed_complete(pos, rbv, delay=longer_delay)
    pos.move(0)
    time.sleep(SHORT_DELAY_FOR_EPICS)
    assert pos.setpoint.get() == 0
    assert pos.position == 0
    assert pos.inposition
