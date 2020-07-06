
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

from apstools.beamtime import bss_info


def using_APS_workstation():
    hostname = socket.gethostname()
    return hostname.lower().endswith(".aps.anl.gov")


class Test_ProgramCommands(unittest.TestCase):

    def setUp(self):
        self.sys_argv0 = sys.argv[0]
        sys.argv = [self.sys_argv0,]

    def tearDown(self):
        sys.argv = [self.sys_argv0,]

    def test_no_options(self):
        args = bss_info.get_options()
        self.assertIsNotNone(args)
        self.assertIsNone(args.subcommand)

    def test_beamlines(self):
        sys.argv.append("beamlines")
        args = bss_info.get_options()
        self.assertIsNotNone(args)
        self.assertEqual(args.subcommand, "beamlines")

    def test_current(self):
        sys.argv.append("current")
        sys.argv.append("9-ID-B,C")
        args = bss_info.get_options()
        self.assertIsNotNone(args)
        self.assertEqual(args.subcommand, "current")
        self.assertEqual(args.beamlineName, "9-ID-B,C")

    def test_cycles(self):
        sys.argv.append("cycles")
        args = bss_info.get_options()
        self.assertIsNotNone(args)
        self.assertEqual(args.subcommand, "cycles")

    def test_esaf(self):
        sys.argv.append("esaf")
        sys.argv.append("12345")
        args = bss_info.get_options()
        self.assertIsNotNone(args)
        self.assertEqual(args.subcommand, "esaf")
        self.assertEqual(args.esafId, 12345)

    def test_proposal(self):
        sys.argv.append("proposal")
        sys.argv.append("proposal_number_here")
        sys.argv.append("1995-1")
        sys.argv.append("my_beamline")
        args = bss_info.get_options()
        self.assertIsNotNone(args)
        self.assertEqual(args.subcommand, "proposal")
        self.assertEqual(args.proposalId, "proposal_number_here")
        self.assertEqual(args.cycle, "1995-1")
        self.assertEqual(args.beamlineName, "my_beamline")

    def test_EPICS_clear(self):
        sys.argv.append("clear")
        sys.argv.append("bss:")
        args = bss_info.get_options()
        self.assertIsNotNone(args)
        self.assertEqual(args.subcommand, "clear")
        self.assertEqual(args.prefix, "bss:")

    def test_EPICS_setup(self):
        sys.argv.append("setup")
        sys.argv.append("bss:")
        sys.argv.append("my_beamline")
        sys.argv.append("1995-1")
        args = bss_info.get_options()
        self.assertIsNotNone(args)
        self.assertEqual(args.subcommand, "setup")
        self.assertEqual(args.prefix, "bss:")
        self.assertEqual(args.beamlineName, "my_beamline")
        self.assertEqual(args.cycle, "1995-1")

    def test_EPICS_update(self):
        sys.argv.append("update")
        sys.argv.append("bss:")
        args = bss_info.get_options()
        self.assertIsNotNone(args)
        self.assertEqual(args.subcommand, "update")
        self.assertEqual(args.prefix, "bss:")


class Test_Beamtime(unittest.TestCase):

    def test_command_options(self):
        self.assertTrue(True)   # test something
        # TODO:

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

        runs = bss_info.listAllRuns()
        self.assertGreater(len(runs), 1)
        self.assertEqual(bss_info.getCurrentCycle(), runs[-1])
        self.assertEqual(bss_info.listRecentRuns()[0], runs[-1])

        self.assertGreater(len(bss_info.listAllBeamlines()), 1)

    def test_printColumns(self):
        from tests.common import Capture_stdout
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
        Test_ProgramCommands,
        ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
