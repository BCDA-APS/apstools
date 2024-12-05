"""
Statistics
====================================================

.. autosummary::

    ~array_index
    ~factor_fwhm
    ~peak_full_width
    ~xy_statistics

"""

import logging
import math

import numpy as np

from .mmap_dict import MMap

logger = logging.getLogger(__name__)
logger.info(__file__)

factor_fwhm = 2 * math.sqrt(2 * math.log(2))
r"""
FWHM :math:`=2\sqrt{2\ln{2}}\cdot\sigma_c`

Conversion factor between full-width at half-maximum peak value and the computed
standard deviation, :math:`\sigma_c`, of the center of mass (centroid),
:math:`\mu`, of the peak.

.. seealso:: https://statproofbook.github.io/P/norm-fwhm.html
"""


def array_index(arr, value) -> int:
    """Return the index for the first occurence of value in arr."""
    return np.where(arr == value)[0][0]


def peak_full_width(x, y, positive=True) -> float:
    """
    Assess *apparent* FWHM by inspecting the data.

    1. Set a goal of half-way between min and max y.

    2. Start at the index of the max (min if positive=False) y.

    3. Find the first indices on low and high side of starting position where
       the goal is passed.  Limited by the range of data available.

    4. For each side, use linear interpolation to compute the x value at the
       goal value.

    5. Compute FWHM as the positive difference between the two sides.

    """
    # Quick, easy decision first:
    if y.min() == y.max():
        return x.max() - x.min()

    goal = (y.max() + y.min()) / 2  # half-max
    logger.debug("searching for apparent peak width: goal=%f", goal)

    value = y.max() if positive else y.min()
    i_lo = array_index(y, value)
    i_hi = i_lo

    if positive:
        while i_lo > 0 and y[i_lo] > goal:
            logger.debug(f"{i_lo=} {i_hi=} {len(y)=}")
            i_lo -= 1
        while i_hi + 1 < len(y) and y[i_hi] > goal:
            i_hi += 1
            logger.debug(f"{i_lo=} {i_hi=} {len(y)=}")
    else:
        while i_lo > 0 and y[i_lo] < goal:
            logger.debug(f"{i_lo=} {i_hi=} {len(y)=}")
            i_lo -= 1
        while i_hi + 1 < len(y) and y[i_hi] < goal:
            i_hi += 1
            logger.debug(f"{i_lo=} {i_hi=} {len(y)=}")

    def interpolate_2_point(value, lo, hi):
        """Could fail if y2 == y1: ZeroDivisionError."""
        lo, hi = sorted([lo, hi])  # take no chances
        x1, x2 = x[lo], x[hi]
        y1, y2 = y[lo], y[hi]
        return (value - y1) * (x2 - x1) / (y2 - y1) + x1

    x_hi = interpolate_2_point(goal, i_hi - 1, i_hi)
    x_lo = interpolate_2_point(goal, i_lo, i_lo + 1)
    fwhm = abs(x_hi - x_lo)  # absolute value, take no chances
    logger.debug("Found apparent FWHM: fwhm=%f", fwhm)
    return fwhm


def xy_statistics(x: list, y: list = None) -> MMap:
    r"""
    Compute statistical measures of a 1-D array (or weighted array), using *numpy*.

    Results are returned in :class:`~apstools.utils.mmap_dict.MMap` dictionary.
    When suppplied, :math:`\vec{y}` will be used as the weights of :math:`\vec{x}`.
    Uses *numpy* [#numpy]_ as an alternative to *PySumReg*. [#PySumReg]_

    .. [#numpy] https://numpy.org/
    .. [#PySumReg] https://prjemian.github.io/pysumreg/index.html

    PARAMETERS

    x : list | numpy.ndarray
        :math:`\vec{x}`: 1-D array of numbers.
    y : list | numpy.ndarray
        :math:`\vec{y}`: (optional) 1-D array of numbers.
        :math:`\vec{x}` and :math:`\vec{y}` must be of the same length.
        Used as weights for :math:`\vec{x}` in fitting analyses.

    .. rubric:: MMap Dictionary Keys

    These keys are always defined.

    ==============  ======  ==============================================
    key             type    description
    ==============  ======  ==============================================
    ``max_x``       float   Maximum value of :math:`\vec{x}`.
    ``mean_x``      float   :math:`\bar{x}`: Mean value of :math:`\vec{x}`.
    ``median_x``    float   Median value of :math:`\vec{x}`.
    ``min_x``       float   Minmum value of :math:`\vec{x}`.
    ``n``           int     :math:`n`: Length of :math:`\vec{x}`.
    ``range_x``     float   Difference between maximum and minimum values of :math:`\vec{x}`.
    ``stddev_x``    float   :math:`\sigma_x` : Standard deviation of :math:`\vec{x}`.
    ==============  ======  ==============================================

    These keys are added when :math:`\vec{y}` is provided.
    Requires :math:`\vec{x}` & :math:`\vec{y}` to be the same length.

    ==============  ======  ==============================================
    key             type    description
    ==============  ======  ==============================================
    ``centroid``    float   :math:`\mu` : Average of :math:`\vec{x}`, weighted by :math:`\vec{y}`. [#centroid]_
    ``fwhm``        float   Apparent width of the peak at half the maximum value of :math:`\vec{y}`. [#fwhm]_
    ``max_y``       float   Maximum value of :math:`\vec{y}`.
    ``mean_y``      float   :math:`\bar{y}`: Mean value of :math:`\vec{y}`.
    ``median_y``    float   Median value of :math:`\vec{y}`.
    ``min_y``       float   Minmum value of :math:`\vec{y}`.
    ``range_y``     float   Difference between maximum and minimum values of :math:`\vec{y}`.
    ``stddev_y``    float   :math:`\sigma_y` : Standard deviation of :math:`\vec{y}`.
    ==============  ======  ==============================================

    .. [#centroid] centroid:  :math:`\mu = {{\sum_i^n{x_i \cdot y_i}} / {\sum_i^n{y_i}}}`

        In the special case when all of :math:`\vec{y}` is zero, :math:`\mu` is
        set to halfway between ``min_x`` and ``max_x``.

        .. seealso:: https://en.wikipedia.org/wiki/Weighted_arithmetic_mean

    .. [#fwhm] FWHM: In the special case when all of :math:`\vec{y}` is zero, ``fwhm`` is set
        to the positive difference of ``max_x`` &  ``min_x``.

    These keys are added when :math:`\vec{y}` is not constant.

    ==============  ======  ==============================================
    key             type    description
    ==============  ======  ==============================================
    ``sigma``       float   :math:`\sigma_c` : Standard error of :math:`\mu`, a statistical measure of the peak width.  See ``variance``.  [#variance]_
    ``variance``    float   :math:`\sigma_c^2`  [#variance]_
    ``x_at_max_y``  float   ``x`` value at maximum of :math:`\vec{y}` array.  For positive-going peaks, this is the "peak position".
    ``x_at_min_y``  float   ``x`` value at minimum of :math:`\vec{y}` array.  For negative-going peaks, this is the "peak position".
    ==============  ======  ==============================================

    .. [#variance] variance: :math:`\sigma_c^2 = {{\sum_i^n{(x_i - \mu)^2 \cdot y_i}} / {\sum_i^n{y_i}}}`

        .. seealso:: https://en.wikipedia.org/wiki/Weighted_arithmetic_mean

    These keys are added when a fit of :math:`\vec{y}` *vs.* :math:`\vec{x}` to
    a first-order polynomial (straight line) and its covariance matrix can be
    computed.

    ======================  ======  ==============================================
    key                     type    description
    ======================  ======  ==============================================
    ``correlation``         float   Correlation coefficient :math:`r`.  Measure of the goodness of fit.
    ``intercept``           float   Computed y-axis intercept when fitting (x,y) to a straight line.
    ``slope``               float   Computed y-axis slope when fitting (x,y) to a straight line.
    ``stddev_intercept``    float   Standard deviation of intercept, from covariance matrix when fitting (x,y) to a straight line.
    ``stddev_slope``        float   Standard deviation of slope, from covariance matrix when fitting (x,y) to a straight line.
    ======================  ======  ==============================================
    """

    x = np.array(x)
    if len(x) == 0:
        raise ValueError("Array x cannot be empty.")

    results = MMap(
        max_x=x.max(),
        mean_x=x.mean(),
        median_x=(x.max() + x.min()) / 2,
        min_x=x.min(),
        n=len(x),
        range_x=x.max() - x.min(),
        stddev_x=x.std(),
    )
    if y is not None:
        y = np.array(y)
        if len(x) != len(y):
            raise ValueError(f"Unequal shapes: {x.shape=} {y.shape=}")

        results.update(
            {
                "max_y": y.max(),
                "mean_y": y.mean(),
                "median_y": (y.max() + y.min()) / 2,
                "min_y": y.min(),
                "range_y": y.max() - y.min(),
                "stddev_y": y.std(),
            }
        )

        if y.min() != y.max():
            results.update(
                {
                    "x_at_min_y": x[array_index(y, y.min())],
                    "x_at_max_y": x[array_index(y, y.max())],
                }
            )
            # Analyze with numpy
            # https://stackoverflow.com/a/2415343/1046449
            center_of_mass = results["centroid"] = np.average(x, weights=y)
            results["fwhm"] = peak_full_width(x, y)
            try:
                results["variance"] = max(
                    0.0,
                    np.average((x - center_of_mass) ** 2, weights=y),
                )
                results["sigma"] = math.sqrt(results["variance"])
            except ValueError as reason:
                logger.warning("Cannot compute variance: %s", reason)
                results["variance"] = 0.0  # define anyway
                results["sigma"] = 0.0

            try:
                results["correlation"] = np.corrcoef(x, y)[0, 1]
                fit = np.polyfit(x, y, 1, cov=True)
                results.update(
                    {
                        "intercept": fit[0][1],
                        "slope": fit[0][0],
                        "stddev_intercept": math.sqrt(fit[1][1, 1]),
                        "stddev_slope": math.sqrt(fit[1][0, 0]),
                    }
                )
            except (TypeError, ValueError) as reason:
                logger.warning("Could not compute covariance matrix: %s", reason)
        else:
            results["centroid"] = (x.max() + x.min()) / 2
            results["fwhm"] = abs(x.max() - x.min())

    return results
