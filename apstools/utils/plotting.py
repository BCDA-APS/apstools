
"""
support for plotting

.. autosummary::
   
   ~plot_prune_fifo
"""

__all__ = ["plot_prune_fifo",]

import logging
logger = logging.getLogger(__name__)


def plot_prune_fifo(bec, n, y, x):
    """
    find the plot with axes x and y and replot with only the last *n* lines

    Note: this is not a bluesky plan.  Call it as normal Python function.

    EXAMPLE::

        plot_prune_fifo(bec, 1, noisy, m1)

    PARAMETERS
    
    bec : object
        instance of BestEffortCallback
    
    n : int
        number of plots to keep
    
    y : object
        instance of ophyd.Signal (or subclass), 
        dependent (y) axis
    
    x : object
        instance of ophyd.Signal (or subclass), 
        independent (x) axis
    """
    assert n >= 0, "n must be 0 or greater"
    for liveplot in bec._live_plots.values():
        lp = liveplot.get(y.name)
        if lp is None:
            logger.debug(f"no LivePlot with name {y.name}")
            continue
        if lp.x != x.name or lp.y != y.name:
            logger.debug(f"no LivePlot with axes ('{x.name}', '{y.name}')")
            continue

        # pick out only the traces that contain plot data
        # skipping the lines that show peak centers
        lines = [
            tr
            for tr in lp.ax.lines
            if len(tr._x) != 2 
                or len(tr._y) != 2 
                or (len(tr._x) == 2 and tr._x[0] != tr._x[1])
        ]
        if len(lines) > n:
            logger.debug(f"limiting LivePlot({y.name}) to {n} traces")
            lp.ax.lines = lines[-n:]
            lp.ax.legend()
            if n > 0:
                lp.update_plot()
        return lp
