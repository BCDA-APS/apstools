"""
Unit testing of plans.
"""

from ... import plans as APS_plans
from bluesky.simulators import summarize_plan

import ophyd.sim
import os
import pytest
import sys


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
    summarize_plan(APS_plans.addDeviceDataAsStream(*objects, name))

    captured = capsys.readouterr()
    assert captured.out == expected


def test_register_action_handler():
    assert summarize_plan != APS_plans.execute_command_list

    APS_plans.register_command_handler(summarize_plan)
    assert APS_plans._COMMAND_HANDLER_ == summarize_plan
    assert APS_plans._COMMAND_HANDLER_ != APS_plans.execute_command_list

    APS_plans.register_command_handler()
    assert APS_plans._COMMAND_HANDLER_ == APS_plans.execute_command_list