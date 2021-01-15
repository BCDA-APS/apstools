"""
simple unit tests for this package
"""

import os
import sys
import unittest

PATH = os.path.dirname(__file__)
_path = os.path.join(PATH, "..")
if _path not in sys.path:
    sys.path.insert(0, _path)

from apstools import utils as APS_utils
from apstools import plans as APS_plans


class Test_CommandList(unittest.TestCase):

    xl_file = os.path.join(PATH, "demo3.xlsx")
    xl_command_file = os.path.join(PATH, "actions.xlsx")
    text_command_file = os.path.join(PATH, "actions.txt")
    missing_file = os.path.join(PATH, "cannot find this")
    not_commands = __file__

    def test_ExcelFile(self):
        # just a spreadsheet for testing (early version of a command file)
        commands = APS_plans.get_command_list(self.xl_file)
        self.assertEqual(len(commands), 9)  # rows
        table = APS_utils.command_list_as_table(commands, show_raw=False)
        received = str(table).strip()
        expected = """
        ====== ====== =========================================
        line # action parameters
        ====== ====== =========================================
        1      row1   91, 26, 85, None, blank, 8
        2      row2   9, 39, 29, 85, sample, 60
        3      row3   54, None, 38, 3, blank, 76
        4      row4   71, 36, 95, 83, foil, 12
        5      row5   55, 75, 59, 84, DNA, 34
        6      row6   18, 49, 31, 34, lecithin, 47
        7      row7   37, None, None, None, a big mix  of stuff
        8      row8   37, 80, 79, 45, salt water, 36
        9      row9   72, 98, 67, 89, surprises, 49
        ====== ====== =========================================
        """.strip()
        self.compare_tables_as_str(expected, received)

    def compare_tables_as_str(self, expected, received):
        e_lines = expected.strip().splitlines()
        r_lines = received.strip().splitlines()
        self.assertEqual(len(e_lines), len(r_lines))
        for expect, got in zip(e_lines, r_lines):
            self.assertEqual(expect.strip(), got.strip())

    def test_ExcelCommandList(self):
        commands = APS_plans.get_command_list(self.xl_command_file)
        self.assertEqual(len(commands), 7)
        table = APS_utils.command_list_as_table(commands, show_raw=False)
        received = str(table).strip()
        expected = """
        ====== ============ ===========================
        line # action       parameters
        ====== ============ ===========================
        1      mono_shutter open
        2      USAXSscan    45.07, 98.3, 0, Water Blank
        3      saxsExp      45.07, 98.3, 0, Water Blank
        4      waxwsExp     45.07, 98.3, 0, Water Blank
        5      USAXSscan    12, 12, 1.2, plastic
        6      USAXSscan    12, 37, 0.1, Al foil
        7      mono_shutter close
        ====== ============ ===========================
        """.strip()
        self.compare_tables_as_str(expected, received)

    def test_TextCommandList(self):
        commands = APS_plans.get_command_list(self.text_command_file)
        self.assertEqual(len(commands), 5)
        table = APS_utils.command_list_as_table(commands, show_raw=False)
        received = str(table).strip()
        expected = """
        ====== ============ ========================
        line # action       parameters
        ====== ============ ========================
        5      sample_slits 0, 0, 0.4, 1.2
        7      preusaxstune
        10     FlyScan      0, 0, 0, blank
        11     FlyScan      5, 2, 0, empty container
        12     SAXS         0, 0, 0, blank
        ====== ============ ========================
        """.strip()
        self.compare_tables_as_str(expected, received)

    def test_TextCommandListRaw(self):
        commands = APS_plans.get_command_list(self.text_command_file)
        self.assertEqual(len(commands), 5)
        table = APS_utils.command_list_as_table(commands, show_raw=True)
        received = str(table).strip()
        expected = """
        ====== ============ ======================== =====================================
        line # action       parameters               raw input
        ====== ============ ======================== =====================================
        5      sample_slits 0, 0, 0.4, 1.2           sample_slits 0 0 0.4 1.2
        7      preusaxstune                          preusaxstune
        10     FlyScan      0, 0, 0, blank           FlyScan 0   0   0   blank
        11     FlyScan      5, 2, 0, empty container FlyScan 5   2   0   "empty container"
        12     SAXS         0, 0, 0, blank           SAXS 0 0 0 blank
        ====== ============ ======================== =====================================
        """.strip()
        self.compare_tables_as_str(expected, received)

    def test_CannotFindFile(self):
        with self.assertRaises(IOError) as context:
            APS_plans.get_command_list(self.missing_file)
        received = str(context.exception)
        expected = "file not found: "
        self.assertTrue(received.startswith(expected))

    def test_NotCommandList(self):
        with self.assertRaises(APS_plans.CommandFileReadError) as context:
            APS_plans.get_command_list(self.not_commands)
        received = str(context.exception)
        expected = "could not read "
        self.assertTrue(received.startswith(expected))


def suite(*args, **kw):
    test_list = [
        Test_CommandList,
    ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(suite())
