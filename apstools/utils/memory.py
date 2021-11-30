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
