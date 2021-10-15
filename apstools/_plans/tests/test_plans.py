"""
Unit testing of plans.
"""

from bluesky.simulators import summarize_plan
from ophyd.signal import EpicsSignalBase

import ophyd.sim
import os
import pytest
import sys

from ... import plans as APS_plans
from ...plans import _COMMAND_HANDLER_
from ...plans import addDeviceDataAsStream
from ...plans import execute_command_list
from ...plans import get_command_list
from ...plans import register_command_handler
from ...plans import run_command_file


# set default timeout for all EpicsSignal connections & communications
try:
    EpicsSignalBase.set_defaults(
        auto_monitor=True, timeout=60, write_timeout=60, connection_timeout=60,
    )
except RuntimeError:
    pass  # ignore if some EPICS object already created


DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "tests")
)


def test_myoutput(capsys):  # or use "capfd" for fd-level
    print("hello")
    sys.stderr.write("world\n")
    captured = capsys.readouterr()
    assert captured.out == "hello\n"
    assert captured.err == "world\n"
    print("next")
    captured = capsys.readouterr()
    assert captured.out == "next\n"


@pytest.mark.parametrize(
    "objects, name, expected",
    [
        ([ophyd.sim.motor1], "test-device", "  Read ['motor1']\n"),
        (
            [[ophyd.sim.motor2, ophyd.sim.motor3]],
            "test-device-list",
            "  Read ['motor2', 'motor3']\n",
        ),
    ],
)
def test_addDeviceDataAsStream(objects, name, expected, capsys):
    summarize_plan(addDeviceDataAsStream(*objects, name))

    captured = capsys.readouterr()
    assert captured.out == expected


def test_register_action_handler():
    assert summarize_plan != execute_command_list
    assert APS_plans._COMMAND_HANDLER_ == _COMMAND_HANDLER_

    register_command_handler(summarize_plan)
    assert APS_plans._COMMAND_HANDLER_ != _COMMAND_HANDLER_  # FIXME:
    assert APS_plans._COMMAND_HANDLER_ == summarize_plan
    assert APS_plans._COMMAND_HANDLER_ != execute_command_list

    register_command_handler()
    assert APS_plans._COMMAND_HANDLER_ == _COMMAND_HANDLER_
    assert APS_plans._COMMAND_HANDLER_ == execute_command_list


def test_get_command_list(capsys):
    filename = os.path.join(DATA_PATH, "actions.txt")
    assert os.path.exists(filename)

    expected = [
        "sample_slits 0 0 0.4 1.2",
        "preusaxstune",
        "FlyScan 0   0   0   blank",
        'FlyScan 5   2   0   "empty container"',
        "SAXS 0 0 0 blank",
    ]

    commands = get_command_list(filename)
    assert len(commands) == len(expected)
    for r, e in zip(commands, expected):
        assert r[-1] == e


def test_run_command_file_text(capsys):
    filename = os.path.join(DATA_PATH, "actions.txt")
    assert os.path.exists(filename)

    expected = [
        f"Command file: {filename}",
        "====== ============ ========================",
        "line # action       parameters              ",
        "====== ============ ========================",
        "5      sample_slits 0, 0, 0.4, 1.2          ",
        "7      preusaxstune                         ",
        "10     FlyScan      0, 0, 0, blank          ",
        "11     FlyScan      5, 2, 0, empty container",
        "12     SAXS         0, 0, 0, blank          ",
        "====== ============ ========================",
        "",
        "file line 5: sample_slits 0 0 0.4 1.2",
        "no handling for line 5: sample_slits 0 0 0.4 1.2",
        "file line 7: preusaxstune",
        "no handling for line 7: preusaxstune",
        "file line 10: FlyScan 0   0   0   blank",
        "no handling for line 10: FlyScan 0   0   0   blank",
        'file line 11: FlyScan 5   2   0   "empty container"',
        'no handling for line 11: FlyScan 5   2   0   "empty container"',
        "file line 12: SAXS 0 0 0 blank",
        "no handling for line 12: SAXS 0 0 0 blank",
    ]

    summarize_plan(run_command_file(filename))

    captured = capsys.readouterr()
    assert isinstance(captured.out, str)

    received = captured.out.strip().split("\n")
    assert len(received) == len(expected)

    for r, e in zip(received[1:], expected[1:]):  # FIXME: first row?
        assert r.find("\n") == -1
        assert r == e


def test_run_command_file_Excel(capsys):
    filename = os.path.join(DATA_PATH, "actions.xlsx")
    assert os.path.exists(filename)

    expected = [
        f"Command file: {filename}",
        "====== ============ ===========================",
        "line # action       parameters                 ",
        "====== ============ ===========================",
        "1      mono_shutter open                       ",
        "2      USAXSscan    45.07, 98.3, 0, Water Blank",
        "3      saxsExp      45.07, 98.3, 0, Water Blank",
        "4      waxwsExp     45.07, 98.3, 0, Water Blank",
        "5      USAXSscan    12, 12, 1.2, plastic       ",
        "6      USAXSscan    12, 37, 0.1, Al foil       ",
        "7      mono_shutter close                      ",
        "====== ============ ===========================",
        "",
        "file line 1: ['mono_shutter', 'open', None, None, None]",
        "no handling for line 1: ['mono_shutter', 'open', None, None, None]",
        "file line 2: ['USAXSscan', 45.07, 98.3, 0, 'Water Blank']",
        "no handling for line 2: ['USAXSscan', 45.07, 98.3, 0, 'Water Blank']",
        "file line 3: ['saxsExp', 45.07, 98.3, 0, 'Water Blank']",
        "no handling for line 3: ['saxsExp', 45.07, 98.3, 0, 'Water Blank']",
        "file line 4: ['waxwsExp', 45.07, 98.3, 0, 'Water Blank']",
        "no handling for line 4: ['waxwsExp', 45.07, 98.3, 0, 'Water Blank']",
        "file line 5: ['USAXSscan', 12, 12, 1.2, 'plastic']",
        "no handling for line 5: ['USAXSscan', 12, 12, 1.2, 'plastic']",
        "file line 6: ['USAXSscan', 12, 37, 0.1, 'Al foil']",
        "no handling for line 6: ['USAXSscan', 12, 37, 0.1, 'Al foil']",
        "file line 7: ['mono_shutter', 'close', None, None, None]",
        "no handling for line 7: ['mono_shutter', 'close', None, None, None]",
    ]

    summarize_plan(run_command_file(filename))

    captured = capsys.readouterr()
    assert isinstance(captured.out, str)

    received = captured.out.strip().split("\n")
    assert len(received) == len(expected)

    for r, e in zip(received[1:], expected[1:]):  # FIXME: first row?
        assert r.find("\n") == -1
        assert r == e
