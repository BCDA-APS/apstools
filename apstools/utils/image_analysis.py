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
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
from numpy.typing import NDArray
from pysumreg import SummationRegisters

logger = logging.getLogger(__name__)
logger.info(__file__)


def analyze_1D(y_arr: Union[List[float], NDArray[np.float64]], x_arr: Optional[Union[List[float], NDArray[np.float64]]] = None) -> Dict[str, float]:
    """
    Measures of 1D data peak center & width.

    Return result is a dictionary prepared by the
    ``to_dict(use_registers=True)`` method of the
    ``pysumreg.SummationRegisters()`` class.

    Parameters
    ----------
    y_arr : Union[List[float], NDArray[np.float64]]
        Array of y values.
    x_arr : Optional[Union[List[float], NDArray[np.float64]]], optional
        Array of x values. If None, uses indices of y_arr, by default None.

    Returns
    -------
    Dict[str, float]
        Dictionary containing statistical analysis results.

    Example::

        {'mean_x': 2.0, 'mean_y': 7.2,
        'stddev_x': 1.5811388300841898, 'stddev_y': 3.3466401061363027,
        'slope': 0.0, 'intercept': 7.2, 'correlation': 0.0,
        'centroid': 2.0, 'sigma': 1.1547005383792515,
        'min_x': 1, 'max_x': 4, 'min_y': 4, 'max_y': 12,
        'x_at_max_y': 2,
        'n': 5, 'X': 10, 'Y': 36, 'XX': 30, 'XY': 72,
        'XXY': 192, 'YY': 304}

    Raises
    ------
    ValueError
        If x_arr and y_arr are not of the same length.
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


def analyze_2D(image: Union[List[List[float]], NDArray[np.float64]]) -> Dict[str, Union[Tuple[float, float], int]]:
    """
    Analyze 2-D (image) data.

    Parameters
    ----------
    image : Union[List[List[float]], NDArray[np.float64]]
        2D array of image data.

    Returns
    -------
    Dict[str, Union[Tuple[float, float], int]]
        Dictionary containing statistical analysis results for both dimensions.

    Example
    -------
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
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
