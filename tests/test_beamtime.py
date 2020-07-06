
"""
unit tests for beamtime info
"""

import datetime
import os
import socket
import sys
import unittest

_test_path = os.path.dirname(__file__)
_path = os.path.join(_test_path, '..')
if _path not in sys.path:
    sys.path.insert(0, _path)

from tests.common import Capture_stdout, Capture_stderr

from apstools.beamtime import bss_info


def using_APS_workstation():
    hostname = socket.gethostname()
    return hostname.lower().endswith(".aps.anl.gov")


class Test_Beamtime(unittest.TestCase):

    def test_general(self):
        self.assertEqual(bss_info.CONNECT_TIMEOUT, 5)
        self.assertEqual(bss_info.POLL_INTERVAL, 0.01)
        self.assertEqual(
            bss_info.DM_APS_DB_WEB_SERVICE_URL,
            "https://xraydtn01.xray.aps.anl.gov:11236")
        self.assertIsNotNone(bss_info.api_bss)
        self.assertIsNotNone(bss_info.api_esaf)

    def test_iso2datetime(self):
        self.assertEqual(
            bss_info.iso2datetime("2020-06-30 12:31:45.067890"),
            datetime.datetime(2020, 6, 30, 12, 31, 45, 67890)
        )

    def test_not_at_aps(self):
        self.assertTrue(True)   # test something
        if using_APS_workstation():
            return

        # do not try to test for fails using dm package, it has no timeout

    def test_only_at_aps(self):
        self.assertTrue(True)   # test something
        if not using_APS_workstation():
            return
        runs = bss_info.api_bss.listRuns()

    def test_printColumns(self):
        with Capture_stdout() as received:
            bss_info.printColumns("1 2 3 4 5 6".split(), numColumns=3, width=3)
        self.assertEqual(len(received), 2)
        self.assertEqual(received[0], "1  3  5  ")
        self.assertEqual(received[1], "2  4  6  ")

        source = "0123456789"
        self.assertEqual(bss_info.trim(source), source)
        self.assertNotEqual(bss_info.trim(source, length=8), source)
        self.assertEqual(bss_info.trim(source, length=8), "01234...")


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
