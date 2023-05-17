"""
Test the shutter classes.
"""

from ophyd import Component
from ophyd import EpicsSignal

from ...tests import IOC
from ...tests import timed_pause
from .. import shutters

PV_BIT = f"{IOC}gp:bit20"
PV_MOTOR = f"{IOC}m16"


def set_and_assert_signal(signal, value):
    if signal.get() != value:
        signal.put(value)
        timed_pause()
    assert signal.get() == value


def operate_shutter(shutter):
    shutter.open()
    timed_pause()
    assert shutter.isOpen
    assert not shutter.isClosed

    shutter.close()
    timed_pause()
    assert not shutter.isOpen
    assert shutter.isClosed


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
