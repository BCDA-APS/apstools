
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

from apstools import utils as APS_utils


class Test_Utils(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_cleanupText(self):
        original = "1. Some text to cleanup #25"
        received = APS_utils.cleanupText(original)
        expected = "1__Some_text_to_cleanup__25"
        self.assertEqual(received, expected)
    
    def test_device_read2table(self):
        from ophyd.sim import motor1
        table = APS_utils.device_read2table(motor1, show_ancient=True, use_datetime=True)
        # print(table)
        expected = """
=============== =====
name            value
=============== =====
motor1          0    
motor1_setpoint 0    
=============== =====
        """.strip()
        # TODO: figure out how to compare with timestamps
        received = "\n".join([v[:21] for v in str(table).strip().splitlines()])
        self.assertEqual(received, expected)    # fails since timestamps do not match

        table = APS_utils.device_read2table(motor1, show_ancient=True, use_datetime=False)
        # expected = """ """.strip()
        received = "\n".join([v[:21] for v in str(table).strip().splitlines()])
        self.assertEqual(received, expected)    # fails since timestamps do not match

        table = APS_utils.device_read2table(motor1, show_ancient=False, use_datetime=False)
        # expected = """ """.strip()
        received = "\n".join([v[:21] for v in str(table).strip().splitlines()])
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
        expected = """
=========== =============================================================================
key         value                                                                        
=========== =============================================================================
beamline_id developer                                                                    
login_id    jemian:wow.aps.anl.gov                                                       
pid         19072                                                                        
proposal_id None                                                                         
scan_id     10                                                                           
version     {'bluesky': '1.5.2', 'ophyd': '1.3.3', 'apstools': '1.1.5', 'epics': '3.3.3'}
=========== =============================================================================
        """.strip()
        self.assertEqual(received, expected)


def suite(*args, **kw):
    test_list = [
        Test_Utils,
        ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
