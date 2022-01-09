"""
Common support of slits

.. autosummary::

    ~SlitGeometry
"""

from collections import namedtuple


# TODO: How to document this structure?
SlitGeometry = namedtuple("SlitGeometry", "hsize vsize hcenter vcenter")
