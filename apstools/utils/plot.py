"""
Plot Support
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~select_mpl_figure
   ~select_live_plot
   ~trim_plot_lines
   ~trim_plot_by_name
"""

import logging


logger = logging.getLogger(__name__)


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
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
