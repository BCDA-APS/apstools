"""
Unit tests for :mod:`~apstools._utils.device_info`.
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor
from ophyd import Signal
from ophyd.signal import EpicsSignalBase
import pandas as pd
import pyRestTable
import pytest

from ...devices import SwaitRecord
from ..device_info import _list_epics_signals
from ..device_info import listdevice
from ..device_info import listdevice_1_5_2
from ..device_info import object_explorer


IOC = "gp:"  # for testing with an EPICS IOC


class MyDevice(Device):
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
        (calcs, 26),
        (calcs.calc5.description, 1),
        (signal, 1),
        (motor, 2),
        (motor.user_setpoint, 1),
    ],
)
def test_listdevice_1_5_2(obj, length):
    result = listdevice_1_5_2(obj)
    assert isinstance(result, pyRestTable.Table)
    assert len(result.labels) == 3
    assert result.labels == ["name", "value", "timestamp"]
    assert len(result.rows) == length


@pytest.mark.parametrize(
    "obj, length",
    [
        (calcs, 26),
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
    "obj, length",
    [
        (calcs, 126),
        (calcs.calc5.description, 1),
        (signal, 0),
        (motor, 19),
        (motor.user_setpoint, 1),
    ],
)
def test_object_explorer(obj, length):
    result = object_explorer(obj)
    assert isinstance(result, pyRestTable.Table)
    assert len(result.labels) == 3
    assert result.labels == ["name", "PV reference", "value"]
    assert len(result.rows) == length


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
    "function, row, column, value",
    [
        (listdevice, 0, "data name", "calcs_calc5_calculated_value"),
        (listdevice, 0, "value", 0.0),
        (listdevice, 25, "data name", "calcs_calc6_channels_L_input_value"),
        (listdevice, 25, "value", 0.0),
        (listdevice_1_5_2, 0, 0, "calcs_calc5_calculated_value"),
        (listdevice_1_5_2, 0, 1, 0.0),
        (listdevice_1_5_2, 25, 0, "calcs_calc6_channels_L_input_value"),
        (listdevice_1_5_2, 25, 1, 0.0),
        (object_explorer, 0, 0, "calc5.alarm_severity"),
        (object_explorer, 0, 1, f"{IOC}userCalc5.SEVR"),
        (object_explorer, 125, 0, "calc6.trace_processing"),
        (object_explorer, 125, 1, f"{IOC}userCalc6.TPRO"),
        (object_explorer, 125, 2, 0),
    ],
)
def test_spotchecks(function, row, column, value):
    if function == listdevice:
        result = function(calcs, scope="read")
    else:
        result = function(calcs)
    if isinstance(result, pd.DataFrame):
        assert result[column][row] == value
    else:
        assert result.rows[row][column] == value
