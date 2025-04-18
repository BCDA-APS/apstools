"""
Common support of slits

.. autosummary::

    ~SlitGeometry
"""

from collections import namedtuple
from typing import NamedTuple


class SlitGeometry(NamedTuple):
    """Slit size and center as a named tuple."""
    width: float
    height: float
    x: float
    y: float


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
