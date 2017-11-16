
# Copyright (c) 2017-, UChicago Argonne, LLC.  See LICENSE file.

import unittest

from . import __init__

if __name__ == '__main__':
    runner=unittest.TextTestRunner(verbosity=2)
    runner.run(__init__.suite())
