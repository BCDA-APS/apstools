"""
Common support of slits

.. autosummary::

    ~SlitGeometry
"""

from collections import namedtuple

SlitGeometry = namedtuple("SlitGeometry", "width height x y")
"Slit size and center as a named tuple"

# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
