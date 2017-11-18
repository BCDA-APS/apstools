
# Copyright (c) 2017-, UChicago Argonne, LLC.  See LICENSE file.

import os
import sys
import unittest

# _path = os.path.join(os.path.dirname(__file__), '..',)
# if _path not in sys.path:
#     sys.path.insert(0, _path)


def suite(*args, **kw):

    import test_simple
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
