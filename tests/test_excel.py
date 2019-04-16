
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

import apstools.utils

class Test_Demo3(unittest.TestCase):
    
    xl_file = os.path.join(PATH, "demo3.xlsx")
    
    def test_ExcelTable_normal_read(self):
        xl = apstools.utils.ExcelDatabaseFileGeneric(self.xl_file)
        self.assertEqual(len(xl.db), 9)             # rows
        self.assertEqual(len(xl.db["0"]), 7)        # columns
        self.assertTrue("Unnamed: 7" in xl.db["0"])
        self.assertEqual(xl.db["0"]["Unnamed: 7"], 8.0)
    
    def test_ExcelTable_ignore_extra_false(self):
        xl = apstools.utils.ExcelDatabaseFileGeneric(self.xl_file, ignore_extra=False)
        self.assertEqual(len(xl.db), 16)            # rows
        self.assertEqual(len(xl.db["0"]), 9)        # columns


def suite(*args, **kw):
    test_list = [
        Test_Demo3,
        ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
