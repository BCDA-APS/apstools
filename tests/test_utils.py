
"""
simple unit tests for this package
"""

import ophyd.sim
import os
import sys
import time
import unittest
import warnings

_path = os.path.join(os.path.dirname(__file__), '..')
if _path not in sys.path:
    sys.path.insert(0, _path)

from apstools import utils as APS_utils
from apstools import __version__ as APS__version__
from tests.common import Capture_stdout


RE = None


class Test_Utils(unittest.TestCase):

    # def setUp(self):
    #     pass
    # 
    # def tearDown(self):
    #     pass
    
    def test_cleanupText(self):
        original = "1. Some text to cleanup #25"
        received = APS_utils.cleanupText(original)
        expected = "1__Some_text_to_cleanup__25"
        self.assertEqual(received, expected)
    
    def test_device_read2table(self):
        motor1 = ophyd.sim.hw().motor1
        table = APS_utils.device_read2table(
            motor1, show_ancient=True, use_datetime=True)
        # print(table)
        expected = (
            "=============== =====\n"
            "name            value\n"
            "=============== =====\n"
            "motor1          0    \n"
            "motor1_setpoint 0    \n"
            "=============== ====="
            )
        # TODO: figure out how to compare with timestamps
        received = "\n".join([
            v[:21] 
            for v in str(table).strip().splitlines()])
        self.assertEqual(received, expected)    # fails since timestamps do not match

        table = APS_utils.device_read2table(
            motor1, show_ancient=True, use_datetime=False)
        # expected = """ """.strip()
        received = "\n".join(
            [v[:21] 
             for v in str(table).strip().splitlines()])
        self.assertEqual(received, expected)    # fails since timestamps do not match

        table = APS_utils.device_read2table(
            motor1, show_ancient=False, use_datetime=False)
        # expected = """ """.strip()
        received = "\n".join([
            v[:21] 
            for v in str(table).strip().splitlines()])
        self.assertEqual(received, expected)    # fails since timestamps do not match

    def test_dictionary_table(self):
        md = {
            'login_id': 'jemian:wow.aps.anl.gov', 
            'beamline_id': 'developer', 
            'proposal_id': None, 
            'pid': 19072, 
            'scan_id': 10, 
            'version': {
                'bluesky': '1.5.2', 
                'ophyd': '1.3.3', 
                'apstools': '1.1.5', 
                'epics': '3.3.3'
                }
              }
        table = APS_utils.dictionary_table(md)
        received = str(table).strip()
        expected = (
            "=========== =============================================================================\n"
            "key         value                                                                        \n"
            "=========== =============================================================================\n"
            "beamline_id developer                                                                    \n"
            "login_id    jemian:wow.aps.anl.gov                                                       \n"
            "pid         19072                                                                        \n"
            "proposal_id None                                                                         \n"
            "scan_id     10                                                                           \n"
            "version     {'bluesky': '1.5.2', 'ophyd': '1.3.3', 'apstools': '1.1.5', 'epics': '3.3.3'}\n"
            "=========== ============================================================================="
        )
        self.assertEqual(received, expected)

    def test_itemizer(self):
        items = [1.0, 1.1, 1.01, 1.001, 1.0001, 1.00001]
        received = APS_utils.itemizer("%.2f", items)
        expected = ["1.00", "1.10", "1.01", "1.00", "1.00", "1.00"]
        self.assertEqual(received, expected)

    def test_print_RE_md(self):
        global RE
        md = {}
        md["purpose"] = "testing"
        md["versions"] = dict(apstools=APS__version__)
        md["something"] = "else"

        with Capture_stdout() as received:
            APS_utils.print_RE_md(md)

        expected = [
            'RunEngine metadata dictionary:',
            '========= ===============================',
            'key       value                          ',
            '========= ===============================',
            'purpose   testing                        ',
            'something else                           ',
            'versions  ======== ======================',
            '          key      value                 ',
            '          ======== ======================',
            f'          apstools {APS__version__}',
            '          ======== ======================',
            '========= ===============================',
            ''
            ]
        self.assertEqual(len(received), len(expected))
        self.assertEqual(received[4].strip(), expected[4].strip())
        self.assertEqual(received[5].strip(), expected[5].strip())
        self.assertEqual(
            received[9].strip(), 
            expected[9].strip()
            )

    def test_pairwise(self):
        items = [1.0, 1.1, 1.01, 1.001, 1.0001, 1.00001, 2]
        received = list(APS_utils.pairwise(items))
        expected = [(1.0, 1.1), (1.01, 1.001), (1.0001, 1.00001)]
        self.assertEqual(received, expected)

    def test_split_quoted_line(self):
        source = 'FlyScan 5   2   0   "empty container"'
        received = APS_utils.split_quoted_line(source)
        self.assertEqual(len(received), 5)
        expected = ['FlyScan', '5', '2', '0', 'empty container']
        self.assertEqual(received, expected)

    def test_trim_string_for_EPICS(self):
        source = "0123456789"
        self.assertLess(len(source), APS_utils.MAX_EPICS_STRINGOUT_LENGTH)
        received = APS_utils.trim_string_for_EPICS(source)
        self.assertEqual(len(source), len(received))
        expected = source
        self.assertEqual(received, expected)

        source = "0123456789"*10
        self.assertGreater(len(source), APS_utils.MAX_EPICS_STRINGOUT_LENGTH)
        received = APS_utils.trim_string_for_EPICS(source)
        self.assertGreater(len(source), len(received))
        expected = source[:APS_utils.MAX_EPICS_STRINGOUT_LENGTH-1]
        self.assertEqual(received, expected)
    
    def test_listobjects(self):
        sims = ophyd.sim.hw().__dict__
        wont_show = ("flyer1", "flyer2", "new_trivial_flyer", "trivial_flyer")
        num = len(sims) - len(wont_show)
        kk = sorted(sims.keys())
        # sims hardware not found by show_ophyd_symbols() in globals!
        table = APS_utils.listobjects(symbols=sims, printing=False)
        self.assertEqual(4, len(table.labels))
        rr = [r[0] for r in table.rows]
        for k in kk:
            msg = f"{k} not found"
            if k not in wont_show:
                self.assertTrue(k in rr, msg)
        self.assertEqual(num, len(table.rows))

    def test_show_ophyd_symbols(self):
        sims = ophyd.sim.hw().__dict__
        wont_show = ("flyer1", "flyer2", "new_trivial_flyer", "trivial_flyer")
        num = len(sims) - len(wont_show)
        kk = sorted(sims.keys())
        # sims hardware not found by show_ophyd_symbols() in globals!
        with warnings.catch_warnings(record=True) as w:
            # Cause all warnings to always be triggered.
            warnings.simplefilter("always")
            table = APS_utils.show_ophyd_symbols(symbols=sims, printing=False)
            assert len(w) == 1
            assert "DEPRECATED" in str(w[-1].message)

    def test_unix(self):
        cmd = 'echo "hello"'
        out, err = APS_utils.unix(cmd)
        self.assertEqual(out, b'hello\n')
        self.assertEqual(err, b"")
        
        cmd = "sleep 0.8 | echo hello"
        t0 = time.time()
        out, err = APS_utils.unix(cmd)
        dt = time.time() - t0
        self.assertGreaterEqual(dt, 0.8)
        self.assertEqual(out, b'hello\n')
        self.assertEqual(err, b"")


class Test_With_Database(unittest.TestCase):

    def setUp(self):
        from tests.test_export_json import get_db
        self.db = get_db()

    # def tearDown(self):
    #     pass

    def test_listruns(self):
        headers = self.db(plan_name="count")
        headers = list(headers)[0:1]
        self.assertEqual(len(headers), 1)
        table = APS_utils.listruns(
            show_command=True,
            printing=False,
            num=10,
            db=self.db,
            )
        self.assertIsNotNone(table)
        self.assertEqual(
            len(table.labels), 
            3+2, 
            "asked for 2 extra columns (total 5)")
        self.assertEqual(
            len(table.rows), 
            10, 
            "asked for 10 rows")
        self.assertLessEqual(
            len(table.rows[1][4]), 
            40, 
            "command row should be 40 char or less")

    def test_replay(self):
        replies = []
        def cb1(key, doc):
            replies.append((key, len(doc)))
        APS_utils.replay(self.db(plan_name="count"), callback=cb1)
        self.assertGreater(len(replies), 0)
        keys = set([v[0] for v in replies])
        for item in "start stop event descriptor datum resource".split():
            msg = f"{item} not in {keys}"
            self.assertIn(item, keys, msg)

        def cb2(key, doc):
            if key == "start":
                replies.append(doc["time"])

        replies = []
        APS_utils.replay(self.db[-1], callback=cb2)
        self.assertEqual(len(replies), 1, "most recent run")

        replies = []
        APS_utils.replay(self.db[-3:], callback=cb2)
        self.assertEqual(len(replies), 3, "most recent 3 runs")

        replies = []
        APS_utils.replay(self.db(plan_name="count"), callback=cb2)
        previous = 0
        for i, v in enumerate(replies):
            msg = f"expect increasing: #{i} : change={v-previous}"
            self.assertGreater(v - previous, 0, msg)
            previous = v

        replies = []
        APS_utils.replay(self.db(plan_name="count"), callback=cb2, sort=False)
        previous = replies[0]+1
        for i, v in enumerate(replies):
            msg = f"expect decreasing: #{i} : change={v-previous}"
            self.assertLess(v - previous, 0, msg)
            previous = v


def suite(*args, **kw):
    test_list = [
        Test_Utils,
        Test_With_Database,
        ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
