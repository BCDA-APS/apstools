"""
Diagnostic Support for Memory
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~rss_mem
"""

import os
import psutil


def rss_mem() -> dict[str, int]:
    """
    Return memory used by this process.

    Returns
    -------
    dict[str, int]
        Dictionary containing memory information with keys:
        - rss: Resident Set Size (physical memory used)
        - vms: Virtual Memory Size (total virtual memory)
        - shared: Shared memory size
        - text: Text segment size
        - lib: Library size
        - data: Data segment size
        - dirty: Dirty pages size
    """
    return psutil.Process(os.getpid()).memory_info()._asdict()


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
