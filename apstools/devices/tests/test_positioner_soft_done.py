from ophyd import EpicsSignal

from ..positioner_soft_done import PVPositionerSoftDone
from ..positioner_soft_done import PVPositionerSoftDoneWithStop
from ...synApps.swait import UserCalcsDevice
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
    """Test Positioner based on two analogout PVs."""
    # fmt: off
    pos = PVPositionerSoftDoneWithStop(
        PV_PREFIX, readback_pv="float1", setpoint_pv="float2", name="pos"
    )
    # fmt: on
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


@pytest.fixture(scope="function")
def calcpos():
    """Test Positioner based on swait (userCalc) PV."""
    user = UserCalcsDevice(IOC, name="user")
    user.wait_for_connection()
    user.enable.put("Enable")

    swait = user.calc10
    swait.wait_for_connection()
    swait.reset()
    swait.calculation.put("A+(B-A)*C")  # incremental move towards the goal
    swait.channels.A.input_pv.put(swait.calculated_value.pvname)  # readback
    # channel B: setpoint
    swait.channels.C.input_value.put(0.9)  # move fraction
    swait.scanning_rate.put(".1 second")

    calcpos = PVPositionerSoftDoneWithStop(
        "",
        readback_pv=swait.calculated_value.pvname,
        setpoint_pv=swait.channels.B.input_value.pvname,
        name="calcpos",
    )
    calcpos.wait_for_connection()
    yield calcpos


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
    # assert status.elapsed >= 0.5  # can't assure for initial move

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


def confirm_in_position(positioner):
    """Apply the 'inposition' property code."""
    reading = positioner.read()
    sp = reading[positioner.setpoint.name]["value"]
    rb = reading[positioner.readback.name]["value"]
    tol = positioner.actual_tolerance
    assert abs(rb - sp) <= tol, f"setpoint={sp}, readback={rb}, tolerance={tol}"


@pytest.mark.local
@pytest.mark.parametrize(
    "target",
    # fmt: off
    [-1] * 3
    + [0] * 5
    + [1, -1, -1, 1, 1, 2, 0, 1, -1, -1]
    + [round(2 + 5 * random.random(), 2), 0.1, -0.15, -1]
    + [0] * 5,
    # fmt: on
)
def test_target_practice(target, rbv, pos):
    """
    Watch for random errors that fail to reach intended target position.

    Test battery is a sequence of target positions, including repeated moves to
    the same location and pathologies involving numerical zero.
    """
    short_delay_for_EPICS_IOC_database_processing()

    def confirm_sequence_timings():
        """Confirm that values are set in this order."""
        reading = pos.read()
        t_rb = reading[pos.readback.name]["timestamp"]
        t_sp = reading[pos.setpoint.name]["timestamp"]
        t_rbv = rbv.read()[rbv.name]["timestamp"]

        assert t_sp <= t_rbv, f"rbv={t_rbv-t_sp}, readback input not updated"
        assert t_rbv <= t_rb, f"rb={t_rb-t_sp}, readback value not updated"

    # start from known position
    known_start_position = -1
    starting_rb_count = pos._rb_count
    starting_sp_count = pos._sp_count

    # initiate the move to the known position
    pos.setpoint.put(known_start_position)
    # short_delay_for_EPICS_IOC_database_processing()
    assert pos._sp_count > starting_sp_count, "cb_setpoint() was not called"

    # complete the initial move by updating the readback signal
    rbv.put(known_start_position)  # note: pos.readback is read-only
    pos.cb_readback()
    short_delay_for_EPICS_IOC_database_processing(1)
    # time.sleep(0.03)
    assert pos._rb_count > starting_rb_count, "cb_readback() was not called"

    # confirm all are ready
    # confirm_sequence_timings()
    confirm_in_position(pos)
    assert pos.setpoint.get(use_monitor=False) == known_start_position
    assert round(pos.readback.get(use_monitor=False), 2) == known_start_position
    assert pos.inposition, f"target={pos.setpoint.get()}, readback={pos.position}"

    # pick a random time to change RBV after the move starts
    rbv_delay = round(0.2 + 0.7 * random.random(), 1)

    # start code that will update the RBV later
    delayed_complete(pos, rbv, delay=rbv_delay)

    # start the move and wait for RBV to be updated
    diff = target - pos.setpoint.get()
    is_new_target = round(abs(diff), 2) > pos.actual_tolerance
    status = pos.move(target)

    short_delay_for_EPICS_IOC_database_processing()

    # assert not delay_active
    assert pos.setpoint.get(use_monitor=False) == target

    # note: pos.position has been failing (issue #668)
    # Replace ``pos.position`` and force a CA get from the IOC.
    assert round(pos.readback.get(use_monitor=False), 2) == target
    if is_new_target:
        confirm_sequence_timings()
    confirm_in_position(pos)
    assert pos.inposition

    assert status.done
    assert status.success


@pytest.mark.local
@pytest.mark.parametrize(
    "target",
    # fmt: off
    [-1] * 3
    + [0] * 5
    + [1, -1, -1, 1, 1, 2, 0, 1, -1, -1]
    + [round(2 + 5 * random.random(), 2), 0.1, -0.15, -1]
    + [0] * 5,
    # fmt: on
)
def test_move_calcpos(target, calcpos):
    """Demonstrate simpler test with positioner that updates its own RBV."""
    status = calcpos.move(target)
    assert status.elapsed > 0, str(status)
    confirm_in_position(calcpos)
    if not calcpos.inposition:
        calcpos.cb_readback()  # nudge it one more time
    assert calcpos.inposition, str(pos)

    time.sleep(0.2)  # pause between tests


@pytest.mark.parametrize(
    # fmt: off
    "target", [-55, -1.2345, -1, -1, -0.1, -0.1, 0, 0, 0, 0.1, 0.1, 1, 1, 1.2345, 55]
    # fmt: on
)
def test_same_position_725(target, calcpos):
    # Before anything is changed.
    confirm_in_position(calcpos)

    # Confirm the initial position is as expected.
    if calcpos.position == target:
        user = UserCalcsDevice(IOC, name="user")
        user.wait_for_connection()
        swait = user.calc10
        # First, move away from the target.
        away_target = -target or 0.1 * (1 + random.random())
        status = calcpos.move(away_target)
        assert status.done
        assert status.elapsed > 0, str(status)
        assert swait.channels.B.input_value.get() == away_target, f"{swait.channels.B.input_value.get()}  {away_target=}  {target=}"
        confirm_in_position(calcpos)

    # Move to the target position.
    status = calcpos.move(target)
    assert status.done
    assert status.elapsed > 0, str(status)
    confirm_in_position(calcpos)

    # Do it again (the reason for issue #725).
    status = calcpos.move(target)
    assert status.done
    assert status.elapsed > 0, str(status)
    confirm_in_position(calcpos)
