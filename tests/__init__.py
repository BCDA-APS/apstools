
#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     prjemian@gmail.com
# :copyright: (c) 2014-2017, Pete R. Jemian
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

# advice: http://stackoverflow.com/questions/191673/preferred-python-unit-testing-framework?rq=1
# advice: http://stackoverflow.com/questions/17001010/how-to-run-unittest-discover-from-python-setup-py-test#21726329
# advice: http://stackoverflow.com/questions/6164004/python-package-structure-setup-py-for-running-unit-tests?noredirect=1&lq=1


import os
import unittest
import sys

_path = os.path.join(os.path.dirname(__file__), '..',)
if _path not in sys.path:
    sys.path.insert(0, _path)


def suite(*args, **kw):
    from tests import test_simple

    test_suite = unittest.TestSuite()
    test_list = [
        test_simple,
        ]

    for test in test_list:
        test_suite.addTest(test.suite())
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
