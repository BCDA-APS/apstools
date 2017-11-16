
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

from APS_BlueSky_tools import zmq_pair


class Test_Something(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_the_ALL_attribute(self):
        self.assertEqual(len(zmq_pair.__all__), 3)
        self.assertEqual(zmq_pair.__all__[0], "ZMQ_Pair")


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
