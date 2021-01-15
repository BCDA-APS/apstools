"""
simple unit tests for this package
"""

import os
import sys
import unittest

_test_path = os.path.dirname(__file__)
_path = os.path.join(_test_path, "..")
if _path not in sys.path:
    sys.path.insert(0, _path)

from apstools import plans as APS_plans

# from apstools import utils as APS_utils
from bluesky.simulators import summarize_plan
import ophyd.sim
from .common import Capture_stdout


class Test_Plans(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_addDeviceDataAsStream(self):
        with Capture_stdout() as received:
            summarize_plan(
                APS_plans.addDeviceDataAsStream(
                    ophyd.sim.motor1, "test-device"
                )
            )

        expected = ["  Read ['motor1']"]
        self.assertEqual(str(received), str(expected))

        with Capture_stdout() as received:
            summarize_plan(
                APS_plans.addDeviceDataAsStream(
                    [ophyd.sim.motor2, ophyd.sim.motor3],
                    "test-device-list",
                )
            )

        expected = [
            "  Read ['motor2', 'motor3']",
        ]
        self.assertEqual(str(received), str(expected))

    def test_register_action_handler(self):
        APS_plans.register_command_handler(summarize_plan)
        self.assertNotEqual(
            APS_plans._COMMAND_HANDLER_, APS_plans.execute_command_list
        )
        self.assertEqual(APS_plans._COMMAND_HANDLER_, summarize_plan)

        APS_plans.register_command_handler()
        self.assertEqual(
            APS_plans._COMMAND_HANDLER_, APS_plans.execute_command_list
        )

    def test_run_command_file(self):
        filename = os.path.join(_test_path, "actions.txt")
        with Capture_stdout() as received:
            summarize_plan(APS_plans.run_command_file(filename))

        # print(f"|{received}|")
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
        for r, e in zip(received, expected):
            self.assertEqual(str(r), str(e))

        filename = os.path.join(_test_path, "actions.xlsx")
        with Capture_stdout() as received:
            summarize_plan(APS_plans.run_command_file(filename))

        # print(f"|{received}|")
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
        for r, e in zip(received, expected):
            self.assertEqual(str(r), str(e))


def suite(*args, **kw):
    test_list = [
        Test_Plans,
    ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
