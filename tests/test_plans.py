
"""
simple unit tests for this package
"""

from io import StringIO
import os
import sys
import unittest

_path = os.path.dirname(__file__)
_path = os.path.join(_path, '..')
if _path not in sys.path:
    sys.path.insert(0, _path)

from apstools import plans as APS_plans
# from apstools import utils as APS_utils
from bluesky.simulators import summarize_plan
import ophyd.sim

class Capture_stdout(list):
    '''
    capture all printed output (to stdout) into list
    
    # http://stackoverflow.com/questions/16571150/how-to-capture-stdout-output-from-a-python-function-call
    '''
    def __enter__(self):
        sys.stdout.flush()
        self._stdout = sys.stdout
        sys.stdout = self._stringio = StringIO()
        return self

    def __exit__(self, *args):
        self.extend(self._stringio.getvalue().splitlines())
        del self._stringio    # free up some memory
        sys.stdout = self._stdout


class Test_Plans(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass
    
    def test_addDeviceDataAsStream(self):
        with Capture_stdout() as printed_lines:
            summarize_plan(
                APS_plans.addDeviceDataAsStream(
                    ophyd.sim.motor1, 
                    "test-device"))

        received = "\n".join([v[:21] for v in str(printed_lines).strip().splitlines()])
        expected = str(["  Read ['motor1']"])
        self.assertEqual(received, expected)

        with Capture_stdout() as lines2:
            summarize_plan(
                APS_plans.addDeviceDataAsStream(
                    [ophyd.sim.motor2, ophyd.sim.motor3], 
                    "test-device-list"))

        print(f"|{lines2}|")
        received = "\n".join([v for v in str(lines2).strip().splitlines()])
        expected = str([
            "  Read ['motor2']",        # TODO: <-- Why?
            "  Read ['motor2', 'motor3']",
            ])
        self.assertEqual(received, expected)


def suite(*args, **kw):
    test_list = [
        Test_Plans,
        ]
    test_suite = unittest.TestSuite()
    for test_case in test_list:
        test_suite.addTest(unittest.makeSuite(test_case))
    return test_suite


if __name__ == "__main__":
    runner=unittest.TextTestRunner()
    runner.run(suite())
