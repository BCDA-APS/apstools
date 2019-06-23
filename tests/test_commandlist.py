
"""
simple unit tests for this package
"""

import os
import sys
import unittest

PATH = os.path.dirname(__file__)
_path = os.path.join(PATH, '..')
if _path not in sys.path:
    sys.path.insert(0, _path)

from apstools import utils as APS_utils
from apstools import plans as APS_plans

class Test_CommandList(unittest.TestCase):
    
    xl_file = os.path.join(PATH, "demo3.xlsx")      # need different demo file
    text_file = os.path.join(PATH, "something.txt") # need different demo file
    missing_file = os.path.join(PATH, "cannot find this")
    not_commands = __file__
    
    def test_ExcelCommandList(self):
        commands = APS_plans.get_command_list(self.xl_file)
        self.assertEqual(len(commands), 9)             # rows
        table = APS_utils.command_list_as_table(commands, show_raw=False)
        received = str(table).strip()
        expected = """
====== ====== =========================================
line # action parameters                               
====== ====== =========================================
1      row1   91, 26.0, 85.0, None, blank, 8.0         
2      row2   9, 39.0, 29.0, 85.0, sample, 60.0        
3      row3   54, None, 38.0, 3.0, blank, 76.0         
4      row4   71, 36.0, 95.0, 83.0, foil, 12.0         
5      row5   55, 75.0, 59.0, 84.0, DNA, 34.0          
6      row6   18, 49.0, 31.0, 34.0, lecithin, 47.0     
7      row7   37, None, None, None, a big mix  of stuff
8      row8   37, 80.0, 79.0, 45.0, salt water, 36.0   
9      row9   72, 98.0, 67.0, 89.0, surprises, 49.0    
====== ====== =========================================
        """.strip()
        self.assertEqual(expected, received)
    
    def test_TextCommandList(self):
        commands = APS_plans.get_command_list(self.text_file)
        table = APS_utils.command_list_as_table(commands, show_raw=False)
        # print(table)
    
    def test_CannotFindFile(self):
        commands = APS_plans.get_command_list(self.missing_file)
        table = APS_utils.command_list_as_table(commands, show_raw=False)
        # print(table)
    
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
    runner=unittest.TextTestRunner()
    runner.run(suite())
