"""
Diagnostic Support for Memory
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~rss_mem
"""

import os
import psutil


def rss_mem():
    """return memory used by this process"""
    return psutil.Process(os.getpid()).memory_info()

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
