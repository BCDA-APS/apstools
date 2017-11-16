
"""
simple unit tests for this package
"""

import os
import sys
import unittest

_path = os.path.dirname(__file__)
_path = os.path.join(_path, '..')
if _path not in sys.path:
    sys.path.insert(0, _path)

import APS_BlueSky_tools


class Test_Something(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_the_ALL_attribute(self):
        self.assertEqual(APS_BlueSky_tools.__project__, u'APS_BlueSky_tools')


def suite(*args, **kw):
    test_suite = unittest.TestSuite()
    test_list = [
        Test_Something,
        ]
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
