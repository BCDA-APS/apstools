
"""
unit tests for beamtime info
"""

import os
import socket
import sys
import unittest

_test_path = os.path.dirname(__file__)
_path = os.path.join(_test_path, '..')
if _path not in sys.path:
    sys.path.insert(0, _path)

from tests.common import Capture_stdout, Capture_stderr

import apstools.beamtime.bss_info


def using_APS_workstation():
    hostname = socket.gethostname()
    return hostname.lower().endswith(".aps.anl.gov")


class Test_Beamtime(unittest.TestCase):

    def test_general(self):
        self.assertEqual(apstools.beamtime.bss_info.CONNECT_TIMEOUT, 5)
        self.assertEqual(apstools.beamtime.bss_info.POLL_INTERVAL, 0.01)

    def test_aps_only(self):
        if not using_APS_workstation():
            self.assertTrue(True)   # test something
            return


def suite(*args, **kw):
    test_list = [
        Test_Beamtime,
        ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
