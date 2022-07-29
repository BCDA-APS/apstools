"""
Unit testing of plans.
"""

from bluesky.simulators import summarize_plan
from ophyd.signal import EpicsSignalBase

import ophyd.sim
import pathlib
import pytest
import sys

from .. import addDeviceDataAsStream
from .. import execute_command_list
from .. import get_command_list
from .. import register_command_handler
from .. import run_command_file
from ...tests import MASTER_TIMEOUT


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


DATA_PATH = pathlib.Path(__file__).parent


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
    from ..command_list import COMMAND_LIST_REGISTRY

    assert COMMAND_LIST_REGISTRY.command == execute_command_list
    assert summarize_plan != execute_command_list

    register_command_handler(summarize_plan)
    assert COMMAND_LIST_REGISTRY.command == summarize_plan
    assert COMMAND_LIST_REGISTRY.command != execute_command_list

    register_command_handler()
    assert COMMAND_LIST_REGISTRY.command == execute_command_list


def test_get_command_list(capsys):
    filename = (DATA_PATH / "actions.txt")
    assert filename.exists()

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
    filename = (DATA_PATH / "actions.txt")
    assert filename.exists()

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
    filename = (DATA_PATH / "actions.xlsx")
    assert filename.exists()

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
