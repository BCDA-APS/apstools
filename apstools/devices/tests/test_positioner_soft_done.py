from ophyd import EpicsSignal

from ..positioner_soft_done import PVPositionerSoftDone
from ..positioner_soft_done import PVPositionerSoftDoneWithStop
from ...tests import common_attribute_quantities_test
from ...tests import IOC
from ...tests import short_delay_for_EPICS_IOC_database_processing
from ...utils import run_in_thread

import pytest
import random
import time

PV_PREFIX = f"{IOC}gp:"
delay_active = False


@pytest.fixture(scope="function")
def pos():
    "positioner to test."
    pos = PVPositionerSoftDoneWithStop(
        PV_PREFIX, readback_pv="float1", setpoint_pv="float2", name="pos"
    )
    pos.wait_for_connection()
    yield pos


@pytest.fixture(scope="function")
def prec():
    "PV precision."
    prec = EpicsSignal(f"{PV_PREFIX}float1.PREC", name="prec")
    prec.wait_for_connection()
    yield prec


@pytest.fixture(scope="function")
def rbv():
    "Writable readback value for tests."
    rbv = EpicsSignal(f"{PV_PREFIX}float1", name="rbv")
    rbv.wait_for_connection()
    yield rbv


@run_in_thread
def delayed_complete(positioner, readback, delay=1):
    "Time-delayed completion of positioner move."
    global delay_active

    delay_active = True
    time.sleep(delay)
    readback.put(positioner.setpoint.get())
    delay_active = False


@run_in_thread
def delayed_stop(positioner, delay=1):
    "Time-delayed stop of positioner."
    time.sleep(delay)
    positioner.stop()


class Tst_PVPos(PVPositionerSoftDone):
    "To pass the readback_pv and setpoint_pv kwargs."

    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, *args, readback_pv="r", setpoint_pv="p", **kwargs)


class Tst_PVPosWStop(PVPositionerSoftDoneWithStop):
    "To pass the readback_pv and setpoint_pv kwargs."

    def __init__(self, prefix, *args, **kwargs):
        super().__init__(prefix, *args, readback_pv="r", setpoint_pv="p", **kwargs)


@pytest.mark.parametrize(
    "device, pv, connect, attr, expected",
    [
        [Tst_PVPos, "", False, "read_attrs", 2],
        [Tst_PVPos, "", False, "configuration_attrs", 3],
        [Tst_PVPos, "", False, "component_names", 6],
        [Tst_PVPosWStop, "", False, "read_attrs", 2],
        [Tst_PVPosWStop, "", False, "configuration_attrs", 3],
        [Tst_PVPosWStop, "", False, "component_names", 6],
    ],
)
def test_attribute_quantities(device, pv, connect, attr, expected):
    """Verify the quantities of the different attributes."""
    common_attribute_quantities_test(device, pv, connect, attr, expected)


@pytest.mark.parametrize(
    "klass, rb, sp",
    [
        [PVPositionerSoftDone, None, None],
        [PVPositionerSoftDone, "", ""],
        [PVPositionerSoftDone, "test", "test"],
        [PVPositionerSoftDoneWithStop, None, None],
        [PVPositionerSoftDoneWithStop, "", ""],
        [PVPositionerSoftDoneWithStop, "test", "test"],
    ],
)
def test_same_sp_and_rb(klass, rb, sp):
    with pytest.raises(ValueError) as exc:
        klass("", readback_pv=rb, setpoint_pv=sp, name="pos")
    assert str(exc.value).endswith("must have different values")


@pytest.mark.parametrize(
    "device, has_inposition",
    [[PVPositionerSoftDone, False], [PVPositionerSoftDoneWithStop, True]],
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


def test_put_and_stop(rbv, prec, pos):
    short_delay_for_EPICS_IOC_database_processing()
    assert pos.tolerance.get() == -1
    assert pos.precision == prec.get()

    # ensure starting value at 0.0
    pos.setpoint.put(0)
    rbv.put(1)  # make the readback to different
    short_delay_for_EPICS_IOC_database_processing()
    assert not pos.inposition

    rbv.put(0)  # make the readback match
    short_delay_for_EPICS_IOC_database_processing()
    assert pos.position == 0.0

    assert pos.done.get() is True
    assert pos.done_value is True
    assert pos.inposition

    # change the setpoint
    pos.setpoint.put(1)
    short_delay_for_EPICS_IOC_database_processing()
    assert not pos.inposition

    # change the readback to match
    rbv.put(1)
    short_delay_for_EPICS_IOC_database_processing()
    assert pos.inposition

    # change the setpoint
    pos.setpoint.put(0)
    short_delay_for_EPICS_IOC_database_processing()
    assert not pos.inposition

    # move the readback part-way, but move is not over yet
    rbv.put(0.5)
    short_delay_for_EPICS_IOC_database_processing()
    assert not pos.inposition

    # force a stop now
    pos.stop()
    short_delay_for_EPICS_IOC_database_processing()
    pos.cb_readback()
    short_delay_for_EPICS_IOC_database_processing()
    assert pos.setpoint.get() == 0.5
    assert pos.readback.get() == 0.5
    assert pos.position == 0.5
    assert pos.inposition


def test_move_and_stop_nonzero(rbv, pos):
    short_delay_for_EPICS_IOC_database_processing()

    # move to non-zero
    longer_delay = 2
    target = round(2 + 5 * random.random(), 2)
    delayed_complete(pos, rbv, delay=longer_delay)
    t0 = time.time()  # time it
    status = pos.move(target)  # readback set by delayed_complete()
    dt = time.time() - t0
    assert status.done
    assert status.success
    assert status.elapsed >= longer_delay
    short_delay_for_EPICS_IOC_database_processing()
    assert dt >= longer_delay
    assert pos.inposition


def test_move_and_stopped_early(rbv, pos):
    short_delay_for_EPICS_IOC_database_processing()

    # first, move to some random, non-zero, initial position
    target = round(2 + 5 * random.random(), 2)
    delayed_complete(pos, rbv, delay=0.5)
    status = pos.move(target)  # readback set by delayed_complete()
    short_delay_for_EPICS_IOC_database_processing()
    assert status.done
    assert status.success
    assert status.elapsed >= 0.5

    # move that is stopped before reaching the target
    longer_delay = 2
    t0 = time.time()  # time it
    delayed_stop(pos, longer_delay)
    assert pos.inposition
    status = pos.move(target - 1)  # readback set by delayed_stop()
    dt = time.time() - t0
    assert status.done
    assert status.success
    assert status.elapsed >= longer_delay
    short_delay_for_EPICS_IOC_database_processing()
    assert dt >= longer_delay
    assert pos.setpoint.get() == target
    assert round(pos.position, 2) == target
    assert pos.inposition


def test_move_to_zero(rbv, pos):
    short_delay_for_EPICS_IOC_database_processing()

    def make_verified_move(target, delay_time):
        # start code that will update the RBV later
        delayed_complete(pos, rbv, delay=delay_time)

        # start the move and wait for RBV to be updated
        status = pos.move(target)

        short_delay_for_EPICS_IOC_database_processing()

        assert status.done
        assert status.success
        # FIXME: Why does this return immediately SOMETIMES in GH Actions workflow?
        assert round(status.elapsed, 1) in (0.0, delay_time)

        # assert not delay_active
        assert pos.setpoint.get() == target

        # verify the readback was updated AFTER the setpoint with correct delay
        dt = (
            pos.readback.read()["pos"]["timestamp"]
            - pos.setpoint.read()["pos_setpoint"]["timestamp"]
        )
        assert round(dt, 1) in (0.0, delay_time), f"dt={dt}, exp={delay_time}"

        # note: pos.position has been failing (issue #668)
        # Replace ``pos.position`` and force a CA get from the IOC.
        assert round(pos.readback.get(use_monitor=False), 2) == target
        assert pos.inposition

    # start from known position
    known_start_position = -1
    pos.setpoint.put(known_start_position)
    rbv.put(known_start_position)  # note: pos.readback is read-only

    # move to 0.0
    make_verified_move(0, 0.2)

    # move to some random, non-zero, position
    make_verified_move(round(2 + 5 * random.random(), 2), 0.5)

    # move back to 0.0
    make_verified_move(0, 2)
