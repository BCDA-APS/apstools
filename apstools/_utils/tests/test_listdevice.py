"""
Unit tests for :mod:`~apstools.utils.listdevice`.
"""

from ophyd import Component
from ophyd import Device
from ophyd import Signal
from ophyd.signal import EpicsSignalBase
import pandas as pd
import pyRestTable
import pytest

from ...devices import SwaitRecord
from ..device_info import listdevice
from ..device_info import object_explorer
from ..device_info import _list_epics_signals


IOC = "gp:"  # for testing with an EPICS IOC


class MyDevice(Device):
    calc5 = Component(SwaitRecord, "5")
    calc6 = Component(SwaitRecord, "6")


@pytest.fixture
def calcs(scope="function"):
    calcs = MyDevice(f"{IOC}userCalc", name="calcs")
    calcs.wait_for_connection()
    return calcs


@pytest.fixture
def signal(scope="function"):
    calcs = Signal(name="signal", value=True)
    return signal


def test_calcs(calcs):
    assert calcs.connected
    assert calcs is not None
    assert isinstance(calcs, Device)


def test_listdevice(calcs):
    result = listdevice(calcs)
    assert isinstance(result, pyRestTable.Table)
    assert len(result.labels) == 3
    assert result.labels == ["name", "value", "timestamp"]
    assert len(result.rows) == 26


def test_object_explorer(calcs):
    result = object_explorer(calcs)
    assert isinstance(result, pyRestTable.Table)
    assert len(result.labels) == 3
    assert result.labels == ["name", "PV reference", "value"]
    assert len(result.rows) == 126


def test__list_epics_signals(calcs, signal):
    result = _list_epics_signals(calcs)
    assert isinstance(result, list)
    assert len(result) == 126
    for item in result:
        assert isinstance(item, EpicsSignalBase)

    result = _list_epics_signals(calcs.calc5.description)
    assert len(result) == 1
    for item in result:
        assert isinstance(item, EpicsSignalBase)

    result = _list_epics_signals(signal)
    assert result is None


@pytest.mark.parametrize(
    "function, row, column, value",
    [
        (listdevice, 0, 0, "calcs_calc5_calculated_value"),
        (listdevice, 0, 1, 0.0),
        (listdevice, 25, 0, "calcs_calc6_channels_L_input_value"),
        (listdevice, 25, 1, 0.0),
        (object_explorer, 0, 0, "calc5.alarm_severity"),
        (object_explorer, 0, 1, f"{IOC}userCalc5.SEVR"),
        (object_explorer, 125, 0, "calc6.trace_processing"),
        (object_explorer, 125, 1, f"{IOC}userCalc6.TPRO"),
        (object_explorer, 125, 2, 0),
    ],
)
def test_spotchecks(function, row, column, value, calcs):
    result = function(calcs)
    assert result.rows[row][column] == value
