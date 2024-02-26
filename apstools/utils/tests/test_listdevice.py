"""
Unit tests for :mod:`~apstools._utils.device_info`.
"""

import pytest
from ophyd import Component
from ophyd import Device
from ophyd import EpicsMotor
from ophyd import EpicsSignal
from ophyd import Signal
from ophyd.signal import EpicsSignalBase

from ...devices import SwaitRecord
from ...tests import IOC_GP
from .._core import TableStyle
from ..device_info import NOT_CONNECTED_VALUE
from ..device_info import _list_epics_signals
from ..device_info import listdevice


class MySignals(Device):
    allowed = Component(Signal, value=True, kind="omitted")
    background = Component(Signal, value=True, kind="normal")
    message = Component(Signal, value="", kind="config")
    tolerance = Component(Signal, value=1, kind="config")
    visible = Component(Signal, value=True, kind="hinted")


class MyDevice(Device):
    signals = Component(MySignals)
    calc5 = Component(SwaitRecord, "5")
    calc6 = Component(SwaitRecord, "6")


class TwoSignalDevice(Device):
    aaa = Component(EpicsSignal, "aaa")
    bbb = Component(EpicsSignal, "bbb")


calcs = MyDevice(f"{IOC_GP}userCalc", name="calcs")
motor = EpicsMotor(f"{IOC_GP}m1", name="motor")
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
    assert isinstance(result, TableStyle.pyRestTable.value)
    assert len(result.rows) == length
    if length > 0:
        assert len(result.labels) == 3
        expected = ["data name", "value", "timestamp"]
        for r in result.labels:
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
    assert isinstance(result, TableStyle.pyRestTable.value)
    assert column in result.labels

    assert row < len(result.rows)
    assert result.rows[row][result.labels.index(column)] == str(value)


@pytest.mark.parametrize(
    "device, scope, ancient, length",
    [
        (calcs, "epics", False, 0),
        (calcs, "epics", True, 126),
        (calcs, "full", False, 5),
        (calcs, "full", True, 131),
        (calcs, "read", False, 2),
        (calcs, "read", True, 4),
        (calcs, None, False, 5),
        (calcs, None, True, 131),
    ],
)
def test_listdevice_filters(device, scope, ancient, length):
    result = listdevice(device, scope, show_ancient=ancient)
    assert len(result.rows) == length


@pytest.mark.parametrize(
    "device, scope, cnames",
    # fmt: off
    [
        (calcs, "full", [
            "calcs.signals.allowed",
            "calcs.signals.background",
            "calcs.signals.message",
            "calcs.signals.tolerance",
            "calcs.signals.visible",
        ]),
        # This is the case that produced issue 640
        (calcs.signals, "full", [
            "calcs.signals.allowed",
            "calcs.signals.background",
            "calcs.signals.message",
            "calcs.signals.tolerance",
            "calcs.signals.visible",
        ]),
    ],
    # fmt: on
)
def test_listdevice_cname(device, scope, cnames):
    result = listdevice(device, scope, show_ancient=False, cname=True)

    col_num = result.labels.index("name")
    values = [row[col_num] for row in result.rows]
    assert values == cnames


@pytest.mark.parametrize(
    "class_, num_lines, nc_item",
    [
        [TwoSignalDevice, 6, 3],
        [MyDevice, 135, 130],
    ],
)
def test_unconnectable(class_, num_lines, nc_item):
    device = class_("", name="device")
    assert not device.connected

    result = str(listdevice(device)).splitlines()
    assert not device.connected
    assert len(result) == num_lines
    assert result[nc_item].split()[1] == NOT_CONNECTED_VALUE


@pytest.mark.parametrize(
    "width",
    [None, 10, 20, 40, 80, 98, 99, 100, 101, 102, 120],
)
def test_maximum_column_width(width):
    device = MySignals(name="device")
    device.message.put("0123456789" * 10)
    assert len(device.message.get()) == 100

    table = listdevice(device, max_column_width=width)
    # assert isinstance(table, TableStyle.pyRestTable)

    result = str(table).splitlines()
    assert len(result) == 4 + len(device.component_names)
    if width is not None:
        for column, content in enumerate(result[0].split()):
            assert len(content) <= (width), f"{column=} {content=}"


@pytest.mark.parametrize(
    "sig, has_cname, has_dname, has_PV",
    [
        [{}, False, True, False],
        [{"cname": True, "dname": False}, True, False, False],
        [{"cname": True}, True, True, False],
        [{"show_pv": False}, False, True, False],
        [{"show_pv": True, "cname": False, "dname": True}, False, True, True],
        [{"show_pv": True, "cname": False}, True, False, True],
        [{"show_pv": True, "cname": True, "dname": False}, True, False, True],
        [{"show_pv": True, "cname": True}, True, False, True],
        [{"show_pv": True, "dname": False}, True, False, True],
        [{"show_pv": True, "dname": True}, True, True, True],
        [{"show_pv": True}, True, False, True],
    ],
)
def test_listdevice_show_pv(sig, has_cname, has_dname, has_PV):
    line = str(listdevice(motor, **sig)).splitlines()[1].strip()
    if has_cname:
        assert line.split()[0] == "name", f"{line=}"
    else:
        assert line.split()[0] != "name", f"{line=}"

    if has_dname:
        assert "data name" in line, f"{line=}"
    else:
        assert "data name" not in line, f"{line=}"

    if has_PV:
        assert "PV" in line, f"{line=}"
    else:
        assert "PV" not in line, f"{line=}"
