"""
Test the shutter classes.
"""

import pytest
from ophyd import Component
from ophyd import EpicsSignal

from ...tests import IOC_GP
from ...tests import timed_pause
from .. import shutters

PV_BIT = f"{IOC_GP}gp:bit20"
PV_MOTOR = f"{IOC_GP}m16"


def set_and_assert_signal(signal, value):
    if signal.get() != value:
        signal.put(value)
        timed_pause()
    assert signal.get() == value


def operate_shutter(shutter):
    shutter.open()
    timed_pause()
    assert shutter.state in ("open", "unknown")
    if shutter.state != "unknown":
        assert shutter.isOpen
        assert not shutter.isClosed

    shutter.close()
    timed_pause()
    assert shutter.state in ("close", "unknown")
    if shutter.state != "unknown":
        assert not shutter.isOpen
        assert shutter.isClosed


@pytest.mark.parametrize("close_pv", [None, "a:close:pv", f"{IOC_GP}XYZ:CLOSE_EPICS.VAL"])
@pytest.mark.parametrize("open_pv", [None, "that:open:pvname", f"{IOC_GP}ABC:OPEN_EPICS.VAL"])
def test_ApsPssShutter(close_pv, open_pv):
    """
    Structure tests only.

    Cannot connect or operate! We don't have the APS when testing!
    """
    prefix = "TEST:"
    shutter = shutters.ApsPssShutter(prefix, name="shutter", close_pv=close_pv, open_pv=open_pv)
    assert not shutter.connected

    close_pv = close_pv or f"{prefix}Close"
    open_pv = open_pv or f"{prefix}Open"
    assert shutter.open_signal.pvname == open_pv
    assert shutter.close_signal.pvname == close_pv


@pytest.mark.parametrize("state_pv", [None, "the:state:pv", "the:state:EPICS_PV", f"{IOC_GP}hutch_BEAM_PRESENT"])
@pytest.mark.parametrize("close_pv", [None, "a:close:pv", f"{IOC_GP}XYZ:CLOSE_EPICS.VAL"])
@pytest.mark.parametrize("open_pv", [None, "that:open:pvname", f"{IOC_GP}ABC:OPEN_EPICS.VAL"])
def test_ApsPssShutterWithStatus(state_pv, close_pv, open_pv):
    """
    Structure tests only.

    Cannot connect or operate! We don't have the APS when testing!
    """
    prefix = "TEST:"
    shutter = shutters.ApsPssShutterWithStatus(
        prefix, state_pv, name="shutter", close_pv=close_pv, open_pv=open_pv
    )
    assert not shutter.connected

    assert shutter.pss_state.pvname == str(state_pv)


def test_EpicsMotorShutter():
    shutter = shutters.EpicsMotorShutter(PV_MOTOR, name="shutter")
    shutter.wait_for_connection()
    shutter.close_value = 1.0  # default
    shutter.open_value = 0.0  # default
    shutter.tolerance = 0.01  # default

    # put the shutter into known state
    set_and_assert_signal(shutter.signal.user_setpoint, shutter.close_value)
    operate_shutter(shutter)


def test_EpicsOnOffShutter():
    shutter = shutters.EpicsOnOffShutter(PV_BIT, name="shutter")
    shutter.close_value = 0  # default
    shutter.open_value = 1  # default

    # put the shutter into known state
    set_and_assert_signal(shutter.signal, shutter.close_value)
    operate_shutter(shutter)


def test_OneEpicsSignalShutter():
    class OneEpicsSignalShutter(shutters.OneSignalShutter):
        signal = Component(EpicsSignal, "")

    shutter = OneEpicsSignalShutter(PV_BIT, name="shutter")
    shutter.wait_for_connection()
    assert shutter.connected

    # put the shutter into known state
    set_and_assert_signal(shutter.signal, shutter.close_value)
    operate_shutter(shutter)


def test_OneSignalShutter():
    shutter = shutters.OneSignalShutter(name="shutter")
    operate_shutter(shutter)


def test_SimulatedApsPssShutterWithStatus():
    shutter = shutters.SimulatedApsPssShutterWithStatus(name="shutter")
    operate_shutter(shutter)
