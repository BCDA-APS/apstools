import math
import time

import pytest
from ophyd import Component
from ophyd import EpicsSignal

from ...synApps.swait import UserCalcsDevice
from ...tests import IOC_GP
from ...tests import common_attribute_quantities_test
from ...tests import rand
from ...tests import timed_pause
from ...utils import run_in_thread
from ..positioner_soft_done import PVPositionerSoftDone
from ..positioner_soft_done import PVPositionerSoftDoneWithStop
from ..positioner_soft_done import TARGET_UNDEFINED

PV_PREFIX = f"{IOC_GP}gp:"
delay_active = False


# fmt: off
POSITION_SEQUENCE = (
    [-1] * 3
    + [0] * 5
    + [1, -1, -1, 1, 1, 2, 0, 1, -1, -1]
    + [round(rand(2, 5), 2), 0.1, -0.15, -1]
    + [0] * 5
    + [-55, -1.2345, -1, -1, -0.1, -0.1, 0, 0, 0, 0.1, 0.1, 1, 1, 1.2345, 55],
)[0]
# fmt: on


@pytest.fixture(scope="function")
def pos():
    """Test Positioner based on two analogout PVs."""
    # fmt: off
    pos = PVPositionerSoftDoneWithStop(
        PV_PREFIX, readback_pv="float1", setpoint_pv="float2", use_target=True, name="pos"
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
    user = UserCalcsDevice(IOC_GP, name="user")
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

    class MyUserCalcPositioner(PVPositionerSoftDoneWithStop):
        actuate = Component(EpicsSignal, swait.process_record.pvname)
        actuate_value = 1

    calcpos = MyUserCalcPositioner(
        "",
        readback_pv=swait.calculated_value.pvname,
        setpoint_pv=swait.channels.B.input_value.pvname,
        name="calcpos",
    )
    calcpos.wait_for_connection()
    yield calcpos


def confirm_in_position(p, dt):
    """Positioner p.readback is close enough to p.setpoint."""
    p.readback.get(use_monitor=False)  # force a read from the IOC
    p.cb_readback()  # update self.done

    # Collect these values at one instant (as close in time as possible).
    # Do not expect any new callbacks during this function.
    dmov = p.done.get()
    rb = p.readback.get()
    sp = p.setpoint.get()
    tol = p.actual_tolerance

    # fmt: off
    diagnostics = (
        f"{p.name=}"
        f"  {rb=:.5f} {sp=:.5f} {tol=}"
        f"  {dt=:.4f}s"
        f"  {p.done=}"
        f"  {p.done_value=}"
        f"  {time.time()=:.4f}"
    )
    # fmt: on

    assert dmov == p.done_value, diagnostics


@run_in_thread
def delayed_complete(positioner, readback, delay=1):
    "Time-delayed completion of positioner move."
    global delay_active

    delay_active = True
    time.sleep(delay)
    readback.put(positioner.setpoint.get(use_monitor=False))
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
    [[PVPositionerSoftDone, True], [PVPositionerSoftDoneWithStop, True]],
)
def test_structure(device, has_inposition):
    "actual PVs not necessary for this test"
    pos = device("", readback_pv="r", setpoint_pv="v", name="pos")
    assert isinstance(pos, device)
    # avoid hasattr() which tries to connect
    assert ("inposition" in dir(pos)) is has_inposition
    assert pos.precision is None
    assert pos.prefix == ""
    assert pos.readback.pvname == "r"
    assert pos.report_dmov_changes.get() is False
    assert pos.setpoint.pvname == "v"
    assert pos.done.get() is True
    assert pos.done_value is True
    assert pos.target.get() == TARGET_UNDEFINED
    assert pos.tolerance.get() == -1


def test_put_and_stop(rbv, prec, pos):
    assert pos.tolerance.get() == -1
    assert pos.precision == prec.get()

    def motion(rb_initial, target, rb_mid=None):
        rbv.put(rb_initial)  # make the readback to different
        pos.setpoint.put(target)
        assert math.isclose(pos.readback.get(use_monitor=False), rb_initial, abs_tol=0.02)
        assert math.isclose(pos.setpoint.get(use_monitor=False), target, abs_tol=0.02)
        assert pos.done.get() != pos.done_value
        assert not pos.inposition

        if rb_mid is not None:
            # move the readback part-way, but move is not over yet
            rbv.put(rb_mid)
            assert math.isclose(pos.readback.get(use_monitor=False), rb_mid, abs_tol=0.02)
            assert not pos.inposition

            # force a stop now
            pos.stop()
            pos.cb_readback()
            assert pos.setpoint.get(use_monitor=False) == rb_mid
            assert pos.readback.get(use_monitor=False) == rb_mid
            assert pos.position == rb_mid
        else:  # interrupted move
            rbv.put(target)  # make the readback match
            rb_new = pos.readback.get(use_monitor=False)
            assert math.isclose(rb_new, target, abs_tol=0.02)

        assert pos.inposition
        assert pos.done_value is True
        pos.cb_readback()
        assert pos.done.get() is True

    motion(1, 0)  # ensure starting value at 0.0
    motion(0, 1)  # new setpoint
    motion(1, 0, 0.5)  # interrupted move


def test_move_and_stop_nonzero(rbv, pos):
    timed_pause()

    # move to non-zero
    longer_delay = 2
    target = round(rand(2, 5), 2)
    delayed_complete(pos, rbv, delay=longer_delay)
    # t0 = time.time()  # time it
    status = pos.move(target)  # readback set by delayed_complete()
    # dt = time.time() - t0
    assert status.done
    assert status.success
    # assert status.elapsed >= longer_delay

    rb_new = pos.readback.get(use_monitor=False)
    arrived = math.isclose(rb_new, target, abs_tol=pos.actual_tolerance)
    assert arrived, f"{target=}"

    # assert dt >= longer_delay
    assert pos.inposition


def test_move_and_stopped_early(rbv, pos):
    def motion(target, delay, interrupt=False):
        """
        Test moving pos to target.  Update rbv after delay.

        If interrupt is True, stop the move before it is done
        (at a time that is less than the 'delay' value).
        """
        timed_pause(0.1)  # allow previous activities to settle down

        t0 = time.time()
        delayed_complete(pos, rbv, delay=delay)
        status = pos.move(target, wait=False)  # readback set by delayed_complete()

        timed_pause(delay / 2 if interrupt else delay + 0.1)
        dt = time.time() - t0
        # fmt: off
        rb_new = pos.readback.get(use_monitor=False)
        arrived = math.isclose(rb_new, target, abs_tol=pos.actual_tolerance)
        # fmt: on
        if interrupt and not status.done:
            assert not status.success
            assert not arrived, f"{dt=:.3f}"
            pos.stop()
        else:
            assert status.done
            assert status.success
            assert arrived
        confirm_in_position(pos, dt)

    target = round(rand(2, 5), 2)
    motion(target, rand(0.4, 0.3))
    motion(target - 1, rand(0.4, 0.3), True)
    motion(target - 1, rand(0.4, 0.3))


@pytest.mark.parametrize("target", POSITION_SEQUENCE)
def test_position_sequence_pos(target, rbv, pos):
    """
    Move pos to reference, then target position.

    Args:
        target (_type_): new position for the move
        rbv (_type_): Signal to set readback for pos
        pos (_type_): positioner based on two float signals
    """

    def motion(p, goal, delay):
        timed_pause(0.1)  # allow previous activities to settle down

        t0 = time.time()
        p.setpoint.put(goal)
        timed_pause(delay)
        assert math.isclose(p.setpoint.get(use_monitor=False), goal, abs_tol=p.actual_tolerance)

        rbv.put(goal)  # note: pos.readback is read-only
        dt = time.time() - t0
        p.cb_readback()
        assert math.isclose(rbv.get(use_monitor=False), goal, abs_tol=p.actual_tolerance)
        confirm_in_position(p, dt)
        assert p.inposition

    known_position = round(rand(-1.1, 0.2), 4)
    delay = round(rand(0.12, 0.2), 2)

    motion(pos, known_position, delay)  # known starting position
    motion(pos, target, delay)
    motion(pos, target, delay)  # issue #725, repeated move to same target


@pytest.mark.parametrize("target", POSITION_SEQUENCE)
def test_position_sequence_calcpos(target, calcpos):
    """
    Move calcpos to reference, then target position.

    Args:
        target (_type_): new position for the move
        calcpos (_type_): positioner based on swait record
    """

    def motion(p, goal):
        timed_pause(0.1)  # allow previous activities to settle down

        t0 = time.time()
        status = p.move(goal)
        dt = time.time() - t0
        assert status.elapsed > 0, str(status)
        assert status.done, str(status)

        p.cb_readback()
        confirm_in_position(p, dt)

        # fmt: off
        assert math.isclose(
            p.setpoint.get(use_monitor=False),
            goal,
            abs_tol=p.actual_tolerance
        ), f"{status=!r}  {dt=}  {goal=}  {p=!r}  {p.actual_tolerance=}"
        # fmt: on

    motion(calcpos, round(rand(-1.1, 0.2), 4))  # known starting position
    motion(calcpos, target)
    motion(calcpos, target)  # issue #725, repeated move to same target
