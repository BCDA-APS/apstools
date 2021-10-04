# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2021, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

import os
import sys
import unittest

_path = os.path.join(os.path.dirname(__file__), "..",)
if _path not in sys.path:
    sys.path.insert(0, _path)


def suite(*args, **kw):

    from tests import test_apsbss
    from tests import test_simple
    from tests import test_utils

    test_list = [
        test_simple,
        test_utils,
        test_apsbss,
    ]

    test_suite = unittest.TestSuite()
    for test in test_list:
        test_suite.addTest(test.suite())
    return test_suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
