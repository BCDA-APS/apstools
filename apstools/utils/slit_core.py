"""
Common support of slits

.. autosummary::

    ~SlitGeometry
"""

from collections import namedtuple


SlitGeometry = namedtuple("SlitGeometry", "width height x y")
"Slit size and center as a named tuple"
