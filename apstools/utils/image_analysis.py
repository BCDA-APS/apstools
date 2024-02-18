"""
Statistical peak analysis functions
+++++++++++++++++++++++++++++++++++++++

Uses *pysumreg* package (https://prjemian.github.io/pysumreg/) to obtain summary
statistics.

.. autosummary::

   ~analyze_1D
   ~analyze_2D
"""

__all__ = """
    analyze_1D
    analyze_2D
""".split()

import logging

import numpy as np
from pysumreg import SummationRegisters

logger = logging.getLogger(__name__)
logger.info(__file__)


def analyze_1D(y_arr, x_arr=None):
    """
    Measures of 1D data peak center & width.

    Return result is a dictionary prepared by the
    ``to_dict(use_registers=True)`` method of the
    ``pysumreg.SummationRegisters()`` class.

    Example::

        {'mean_x': 2.0, 'mean_y': 7.2,
        'stddev_x': 1.5811388300841898, 'stddev_y': 3.3466401061363027,
        'slope': 0.0, 'intercept': 7.2, 'correlation': 0.0,
        'centroid': 2.0, 'sigma': 1.1547005383792515,
        'min_x': 1, 'max_x': 4, 'min_y': 4, 'max_y': 12,
        'x_at_max_y': 2,
        'n': 5, 'X': 10, 'Y': 36, 'XX': 30, 'XY': 72,
        'XXY': 192, 'YY': 304}
    """
    if x_arr is None:
        x_arr = list(range(len(y_arr)))
    if len(x_arr) != len(y_arr):
        raise ValueError("x and y arrays are not of the same length.")

    regs = SummationRegisters()
    regs.clear()
    for u, v in zip(x_arr, y_arr):
        regs.add(u, v)

    return regs.to_dict(use_registers=True)


def analyze_2D(image):
    """
    Analyze 2-D (image) data.

    Return result is a dictionary with the statistical results for a peak
    analysis, grouped in pairs (row, column) as it makes sense given
    ``frame[rows][columns]``.
    The :math:`x` values are the index number along the respective axis.

    For this image data::

        [
            [0, 1, 2, 1, 0],
            [1, 2, 3, 2, 1],
            [2, 3, 4, 10, 2],
            [1, 2, 3, 2, 1],
        ]

    This is the analysis::

        {'n': (5, 4),
         'centroid': (2.1628, 1.814),
         'sigma': (1.1192, 0.8695),
         'peak_position': (3, 2),
         'max_y': 10}
    """
    if not isinstance(image, np.ndarray):
        image = np.array(image)

    axis_0 = analyze_1D(image.sum(axis=0))
    axis_1 = analyze_1D(image.sum(axis=1))
    key_list = "n centroid sigma".split()
    results = {k: (axis_0[k], axis_1[k]) for k in key_list}
    k = "x_at_max_y"
    results["peak_position"] = (axis_0[k], axis_1[k])
    results["max_y"] = image[axis_1[k]][axis_0[k]]
    return results


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
