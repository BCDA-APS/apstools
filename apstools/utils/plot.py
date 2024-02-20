"""
Plot Support
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~plotxy
   ~select_mpl_figure
   ~select_live_plot
   ~trim_plot_lines
   ~trim_plot_by_name
"""

import datetime
import logging
import math

logger = logging.getLogger(__name__)


def plotxy(runs, xname, yname, append=False, cat=None, stats=True, stream="primary", title=None):
    """
    Plot y vs x from a bluesky run.

    Note: This is not a bluesky plan.  Call it as a normal Python function.

    PARAMETERS

    ``runs`` : *[run]* or *run*:
        List or runs or single ``run``.  A ``run`` is either a
        ``bluesky.core.BlueskyRun`` object or a reference (uid, scan_id,
        relative to most recent) to a BlueskyRun in the catalog.
    ``xname`` : *str*:
        Name of the signal to plot on the **x** axis.
    ``yname`` : *str*:
        Name of the signal to plot on the **y** axis.
    ``append`` : *bool*:
        (optional) If ``True``, append to existing plot window.
        Default: ``append=False``
    ``cat`` : *object*:
        (optional) Catalog to be used for finding a run by reference.
        Default: return value from ``apstools.utils.getCatalog()``
    ``stats`` : *bool*:
        (optional) If ``True``, compute and plot centroid and FWHM
        (computed from sigma).
        Default: ``stats=True``
    ``stream`` : *str*:
        (optional) Name of the data stream in which to find "xname"
        and "yname".
        Default: ``stream="primary"``
    ``title`` : *str*:
        (optional) Title to show on this plot.
        Default: Metadata "title" keyword of first run (if found)
        or scan_id and starting date/time of first run.

    RETURNS

    Returns a *dict* of statistics for each run indexed by ``scan_id``,
    if ``stats=True``, else ``None``.  A computed ``fwhm`` key is added
    to the statistics.

    New in release 1.6.10.
    """
    import matplotlib.pyplot as plt

    from . import getDefaultCatalog

    plt.ion()

    if not isinstance(runs, (list, tuple, range)):
        runs = [runs]

    fig_name = f"plotxy: {yname} v {xname}"
    plt.figure(fig_name)
    if not append:
        plt.autoscale()
        plt.cla()  # reset to autoscale both x & y

    statistics = {}
    for i, run in enumerate(runs):
        if isinstance(run, (str, int)):
            cat = cat or getDefaultCatalog()
            run = cat.v2[run]

        md = run.metadata
        scan_id = md["start"]["scan_id"]
        plan_name = md["start"].get("plan_name", "")

        dataset = getattr(run, stream).read()
        x = dataset[xname]
        y = dataset[yname]
        plt.plot(x.values, y.values, label=f"#{scan_id}: {plan_name}")

        dt = datetime.datetime.fromtimestamp(md["start"]["time"])
        if i == 0:
            if title is None:
                title = md["start"].get("title")
            plt.title(f"#{scan_id}: {dt.isoformat(sep=' ')}")
            if title is not None:
                plt.suptitle(title)
            plt.xlabel(x.name)
            plt.ylabel(y.name)

        if stats:
            import pysumreg

            # collect peak (and other) statistics
            # fmt: off
            sr = pysumreg.SummationRegisters()
            for xv, yv, in zip(x.values, y.values):
                sr.add(xv, yv)
            # fmt: on

            centroid = sr.centroid
            sigma = sr.sigma
            half_max = (sr.max_y if sr.mean_y > 0 else sr.min_y) / 2
            # https://brainder.org/2011/08/20/gaussian-kernels-convert-fwhm-to-sigma/
            fwhm = 2 * math.sqrt(2 * math.log(2)) * sigma
            plt.plot(
                [centroid] * 2, [sr.min_y, sr.max_y], color="gray", linestyle=":", label=f"_{scan_id}_centroid"
            )
            plt.plot(
                [centroid - fwhm / 2, centroid + fwhm / 2],
                [half_max] * 2,
                color="gray",
                linestyle=":",
                label=f"_{scan_id}_sigma",
            )
            statistics[scan_id] = sr.to_dict()
            statistics[scan_id]["fwhm"] = fwhm  # add to dictionary

    plt.legend()
    plt.text(
        plt.axis()[1],
        plt.axis()[2],  # inside lower-right corner
        datetime.datetime.now(),
        fontsize="xx-small",
        color="gray",
        horizontalalignment="right",
    )
    if len(statistics):
        return statistics


def select_mpl_figure(x, y):
    """
    Get the MatPlotLib Figure window for y vs x.

    PARAMETERS

    x
        *object*:
        X axis object (an ``ophyd.Signal``)
    y
        ophyd object:
        X axis object (an ``ophyd.Signal``)

    RETURNS

    object or ``None``:
        Instance of ``matplotlib.pyplot.Figure()``
    """
    import matplotlib.pyplot as plt

    figure_name = f"{y.name} vs {x.name}"
    if figure_name in plt.get_figlabels():
        return plt.figure(figure_name)


def select_live_plot(bec, signal):
    """
    Get the *first* live plot that matches ``signal``.

    PARAMETERS

    bec
        *object*:
        instance of ``bluesky.callbacks.best_effort.BestEffortCallback``
    signal
        *object*:
        The Y axis object (an ``ophyd.Signal``)

    RETURNS

    *object*:
        Instance of ``bluesky.callbacks.best_effort.LivePlotPlusPeaks()``
        or ``None``
    """
    for live_plot_dict in bec._live_plots.values():
        live_plot = live_plot_dict.get(signal.name)
        if live_plot is not None:
            return live_plot


def trim_plot_lines(bec, n, x, y):
    """
    Find the plot with axes x and y and replot with at most the last *n* lines.

    Note: :func:`trim_plot_lines` is not a bluesky plan.  Call it as
    normal Python function.

    EXAMPLE::

        trim_plot_lines(bec, 1, m1, noisy)

    PARAMETERS

    bec
        *object* :
        instance of BestEffortCallback

    n
        *int* :
        number of plots to keep

    x
        *object* :
        instance of ophyd.Signal (or subclass),
        independent (x) axis

    y
        *object* :
        instance of ophyd.Signal (or subclass),
        dependent (y) axis

    (new in release 1.3.5)
    """
    liveplot = select_live_plot(bec, y)
    if liveplot is None:
        logger.debug("no live plot found with signal '%s'", y.name)
        return

    fig = select_mpl_figure(x, y)
    if fig is None:
        logger.debug("no figure found with '%s vs %s'", y.name, x.name)
        return
    if len(fig.axes) == 0:
        logger.debug("no plots on figure: '%s vs %s'", y.name, x.name)
        return

    ax = fig.axes[0]
    while len(ax.lines) > n:
        try:
            ax.lines[0].remove()
        except ValueError as exc:
            if not str(exc).endswith("x not in list"):
                # fmt: off
                logger.warning(
                    "%s vs %s: mpl remove() error: %s",
                    y.name, x.name, str(exc),
                )
                # fmt: on
    ax.legend()
    liveplot.update_plot()
    logger.debug("trim complete")


def trim_plot_by_name(n=3, plots=None):
    """
    Find the plot(s) by name and replot with at most the last *n* lines.

    Note: this is not a bluesky plan.  Call it as normal Python function.

    It is recommended to call :func:`~trim_plot_by_name()` *before* the
    scan(s) that generate plots.  Plots are generated from a RunEngine
    callback, executed *after* the scan completes.

    PARAMETERS

    n
        *int* :
        number of plots to keep

    plots
        *str*, [*str*], or *None* :
        name(s) of plot windows to trim
        (default: all plot windows)

    EXAMPLES::

        trim_plot_by_name()   # default of n=3, apply to all plots
        trim_plot_by_name(5)  # change from default of n=3
        trim_plot_by_name(5, "noisy_det vs motor")  # just this plot
        trim_plot_by_name(
            5,
            ["noisy_det vs motor", "det noisy_det vs motor"]]
        )

    EXAMPLE::

        # use simulators from ophyd
        from bluesky import plans as bp
        from bluesky import plan_stubs as bps
        from ophyd.sim import *

        snooze = 0.25

        def scan_set():
            trim_plot_by_name()
            yield from bp.scan([noisy_det], motor, -1, 1, 5)
            yield from bp.scan([noisy_det, det], motor, -2, 1, motor2, 3, 1, 6)
            yield from bps.sleep(snooze)

        # repeat the_scans 15 times
        uids = RE(bps.repeat(scan_set, 15))

    (new in release 1.3.5)
    """
    import matplotlib.pyplot as plt

    if isinstance(plots, str):
        plots = [plots]

    for fig_name in plt.get_figlabels():
        if plots is None or fig_name in plots:
            fig = plt.figure(fig_name)
            for ax in fig.axes:
                while len(ax.lines) > n:
                    ax.lines[0].remove()
                # update the plot legend
                ax.legend()


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
