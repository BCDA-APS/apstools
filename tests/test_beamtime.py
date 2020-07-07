
"""
unit tests for beamtime info
"""

import datetime
import os
import socket
import subprocess
import sys
import unittest
import uuid

_test_path = os.path.dirname(__file__)
_path = os.path.join(_test_path, '..')
if _path not in sys.path:
    sys.path.insert(0, _path)

from apstools.beamtime import bss_info, bss_info_makedb

BSS_TEST_IOC_PREFIX = f"tst{uuid.uuid4().hex[:7]}:bss:"


def using_APS_workstation():
    hostname = socket.gethostname()
    return hostname.lower().endswith(".aps.anl.gov")


def bss_IOC_available():
    import epics
    # try connecting with one of the PVs in the database
    cycle = epics.PV(f"{BSS_TEST_IOC_PREFIX}esaf:cycle")
    cycle.wait_for_connection(timeout=2)
    return cycle.connected


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

        runs = bss_info.listAllRuns()
        self.assertGreater(len(runs), 1)
        self.assertEqual(bss_info.getCurrentCycle(), runs[-1])
        self.assertEqual(bss_info.listRecentRuns()[0], runs[-1])

        self.assertGreater(len(bss_info.listAllBeamlines()), 1)

        # TODO: test the other functions
        # getCurrentEsafs
        # getCurrentInfo
        # getCurrentProposals
        # getEsaf
        # getProposal
        # class DmRecordNotFound(Exception): ...
        # class EsafNotFound(DmRecordNotFound): ...
        # class ProposalNotFound(DmRecordNotFound): ...

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


class Test_EPICS(unittest.TestCase):

    def start_ioc_subprocess(self, db_file):
        softIoc = os.path.abspath(os.path.join(
            os.environ.get("CONDA_PREFIX"),
            "epics",
            "bin",
            os.environ.get("EPICS_HOST_ARCH", "linux-x86_64"),
            "softIoc"
        ))
        if not os.path.exists(softIoc):
            return
        db_file = os.path.abspath(os.path.join(
            os.path.dirname(bss_info.__file__),
            db_file
        ))
        if not os.path.exists(db_file):
            return
        cmd = f"{softIoc} -m P={BSS_TEST_IOC_PREFIX} -d {db_file}".split()
        return subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False)

    def setUp(self):
        self.bss = None
        self.ioc_process = self.start_ioc_subprocess("bss_info.db")

    def tearDown(self):
        if self.bss is not None:
            self.bss.destroy()
            self.bss = None
        if self.ioc_process is not None:
            self.ioc_process.communicate('exit\n'.encode())
            self.ioc_process = None

    def test_ioc(self):
        if not bss_IOC_available():
            return

        from apstools.beamtime import bss_info_ophyd as bio
        self.bss = bio.EpicsBssDevice(BSS_TEST_IOC_PREFIX, name="bss")
        self.bss.wait_for_connection(timeout=2)
        self.assertTrue(self.bss.connected)

        self.assertEqual(self.bss.esaf.aps_cycle.get(), "")

    def test_EPICS(self):
        from tests.common import Capture_stdout

        if not bss_IOC_available():
            return

        beamline = "9-ID-B,C"
        cycle = "2019-3"

        with Capture_stdout():
            self.bss = bss_info.connect_epics(BSS_TEST_IOC_PREFIX)
        self.assertTrue(self.bss.connected)
        self.assertEqual(self.bss.esaf.aps_cycle.get(), "")

        self.bss.esaf.aps_cycle.put(cycle)
        self.assertNotEqual(self.bss.esaf.aps_cycle.get(), "")

        if not using_APS_workstation():
            return

        # setup
        with Capture_stdout():
            bss_info.epicsSetup(BSS_TEST_IOC_PREFIX, beamline, cycle)
        self.assertNotEqual(self.bss.proposal.beamline_name.get(), "harpo")
        self.assertEqual(self.bss.proposal.beamline_name.get(), beamline)
        self.assertEqual(self.bss.esaf.aps_cycle.get(), cycle)
        self.assertEqual(self.bss.esaf.sector.get(), beamline.split("-")[0])

        # epicsUpdate
        # Example ESAF on sector 9

        # ====== ======== ========== ========== ==================== =================================
        # id     status   start      end        user(s)              title
        # ====== ======== ========== ========== ==================== =================================
        # 226319 Approved 2020-05-26 2020-09-28 Ilavsky,Maxey,Kuz... Commission 9ID and USAXS
        # ====== ======== ========== ========== ==================== =================================

        # ===== ====== =================== ==================== ========================================
        # id    cycle  date                user(s)              title
        # ===== ====== =================== ==================== ========================================
        # 64629 2019-2 2019-03-01 18:35:02 Ilavsky,Okasinski    2019 National School on Neutron & X-r...
        # ===== ====== =================== ==================== ========================================
        esaf_id = "226319"
        proposal_id = "64629"
        self.bss.esaf.aps_cycle.put("2019-2")
        self.bss.esaf.esaf_id.put(esaf_id)
        self.bss.proposal.proposal_id.put(proposal_id)
        with Capture_stdout():
            bss_info.epicsUpdate(BSS_TEST_IOC_PREFIX)
        self.assertEqual(
            self.bss.esaf.title.get(),
            "Commission 9ID and USAXS")
        self.assertTrue(
            self.bss.proposal.title.get().startswith(
            "2019 National School on Neutron & X-r"))

        with Capture_stdout():
            bss_info.epicsClear(BSS_TEST_IOC_PREFIX)
        self.assertNotEqual(self.bss.esaf.aps_cycle.get(), "")
        self.assertEqual(self.bss.esaf.title.get(), "")
        self.assertEqual(self.bss.proposal.title.get(), "")


class Test_MakeDatabase(unittest.TestCase):

    def test_general(self):
        from tests.common import Capture_stdout
        with Capture_stdout() as db:
            bss_info_makedb.main()
        self.assertEqual(len(db), 345)
        self.assertEqual(db[0], "#")
        self.assertEqual(db[1], "# file: bss_info.db")
        # randomly-selected spot checks
        self.assertEqual(db[22], 'record(stringout, "$(P)esaf:id")')
        self.assertEqual(db[128], '    field(ONAM, "ON")')
        self.assertEqual(db[265], '    field(FTVL, "CHAR")')


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


def suite(*args, **kw):
    test_list = [
        Test_Beamtime,
        Test_EPICS,
        Test_MakeDatabase,
        Test_ProgramCommands,
        ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
