
# Copyright (c) 2017-2019, UChicago Argonne, LLC.  See LICENSE file.

import os
import sys
import unittest

_path = os.path.join(os.path.dirname(__file__), '..',)
if _path not in sys.path:
    sys.path.insert(0, _path)


def suite(*args, **kw):

    from tests import test_simple
    from tests import test_filewriter
    from tests import test_export_json
    from tests import test_exceltable
    from tests import test_commandlist
    from tests import test_utils
    test_list = [
        test_simple,
        test_filewriter,
        test_export_json,
        test_exceltable,
        test_commandlist,
        test_utils,
        ]

    test_suite = unittest.TestSuite()
    for test in test_list:
        test_suite.addTest(test.suite())
    return test_suite


if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(suite())
