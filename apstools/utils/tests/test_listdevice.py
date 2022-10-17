"""
Unit tests for :mod:`~apstools._utils.device_info`.
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor
from ophyd import Signal
from ophyd.signal import EpicsSignalBase
import pandas as pd
import pytest

from ...devices import SwaitRecord
from ...tests import MASTER_TIMEOUT
from ..device_info import _list_epics_signals
from ..device_info import listdevice


# set default timeout for all EpicsSignal connections & communications
try:
    EpicsSignalBase.set_defaults(
        auto_monitor=True,
        timeout=MASTER_TIMEOUT,
        write_timeout=MASTER_TIMEOUT,
        connection_timeout=MASTER_TIMEOUT,
    )
except RuntimeError:
    pass  # ignore if some EPICS object already created


IOC = "gp:"  # for testing with an EPICS IOC


class MySignals(Device):
    allowed = Component(Signal, value=True, kind="omitted")
    background = Component(Signal, value=True, kind="normal")
    tolerance = Component(Signal, value=1, kind="config")
    visible = Component(Signal, value=True, kind="hinted")


class MyDevice(Device):
    signals = Component(MySignals)
    calc5 = Component(SwaitRecord, "5")
    calc6 = Component(SwaitRecord, "6")


calcs = MyDevice(f"{IOC}userCalc", name="calcs")
motor = EpicsMotor(f"{IOC}m1", name="motor")
signal = Signal(name="signal", value=True)

calcs.wait_for_connection()
motor.wait_for_connection()


def test_calcs():
    assert calcs.connected
    assert calcs is not None
    assert isinstance(calcs, Device)


@pytest.mark.parametrize(
    "obj, length",
    [
        (calcs, 4),
        (calcs.calc5.description, 1),
        (signal, 1),
        (motor, 2),
        (motor.user_setpoint, 1),
    ],
)
def test_listdevice(obj, length):
    result = listdevice(obj, scope="read")
    assert isinstance(result, pd.DataFrame)
    assert len(result) == length
    if length > 0:
        assert len(result.columns) == 3
        expected = ["data name", "value", "timestamp"]
        for r in result.columns:
            assert r in expected


@pytest.mark.parametrize(
    "obj, length, ref",
    [
        (calcs, 126, EpicsSignalBase),
        (calcs.calc5.description, 1, EpicsSignalBase),
        (signal, None, None),
        (motor, 19, EpicsSignalBase),
        (motor.user_setpoint, 1, EpicsSignalBase),
    ],
)
def test__list_epics_signals(obj, length, ref):
    result = _list_epics_signals(obj)
    if length is None:
        assert result is None
    else:
        assert isinstance(result, list)
        assert len(result) == length
        for item in result:
            assert isinstance(item, ref)


@pytest.mark.parametrize(
    "scope, row, column, value",
    [
        (None, 0, "data name", "motor"),
        (None, 0, "value", 0.0),
        ("epics", 0, "data name", "motor"),
        ("epics", 0, "value", 0.0),
        ("epics", 7, "data name", "motor_acceleration"),
        ("epics", 7, "value", 0.2),
        ("epics", 8, "data name", "motor_motor_egu"),
        ("epics", 8, "value", "degrees"),
        ("full", 0, "data name", "motor"),
        ("full", 0, "value", 0.0),
        ("full", 12, "data name", "motor_low_limit_switch"),
        ("full", 12, "value", 0),
        ("read", 0, "data name", "motor"),
        ("read", 0, "value", 0.0),
    ],
)  # scope: full epics read
def test_spotchecks(scope, row, column, value):
    assert calcs.connected
    if round(motor.position, 2) != 0:
        motor.move(0)
    result = listdevice(motor, scope=scope)
    assert isinstance(result, pd.DataFrame)
    assert column in result
    assert row in result[column]
    assert result[column][row] == value


@pytest.mark.parametrize(
    "device, scope, ancient, length",
    [
        (calcs, "epics", False, 0),
        (calcs, "epics", True, 126),
        (calcs, "full", False, 4),
        (calcs, "full", True, 130),
        (calcs, "read", False, 2),
        (calcs, "read", True, 4),
        (calcs, None, False, 4),
        (calcs, None, True, 130),
    ],
)
def test_listdevice_filters(device, scope, ancient, length):
    result = listdevice(device, scope, show_ancient=ancient)
    assert len(result) == length


@pytest.mark.parametrize(
    "device, scope, cnames",
    [
        (calcs, "full", [
            "calcs.signals.allowed",
            "calcs.signals.background",
            "calcs.signals.tolerance",
            "calcs.signals.visible",
        ]),
        # This is the case that produced issue 640
        (calcs.signals, "full", [
            "calcs.signals.allowed",
            "calcs.signals.background",
            "calcs.signals.tolerance",
            "calcs.signals.visible",
        ]),
    ],
)
def test_listdevice_cname(device, scope, cnames):
    result = listdevice(device, scope, show_ancient=False, cname=True)
    assert result["name"].tolist() == cnames
