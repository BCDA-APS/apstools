"""
Collect statistics on the signals used in 1-D scans.
====================================================

.. autosummary::

    ~factor_fwhm
    ~SignalStatsCallback
"""

__all__ = """
factor_fwhm
SignalStatsCallback
""".split()

import math
import logging

import pyRestTable
import pysumreg

logger = logging.getLogger(__name__)
logger.info(__file__)

factor_fwhm = 2 * math.sqrt(2 * math.log(2))
r"""
FWHM :math:`=2\sqrt{2\ln{2}}\cdot\sigma_c`

see: https://statproofbook.github.io/P/norm-fwhm.html
"""


class SignalStatsCallback:
    """
    Callback: Collect peak (& other) statistics during a scan.

    .. caution:: This is an early draft and is subject to change!

    Subscribe the ``receiver()`` method. Use with step scan plans such as
    ``bp.scan()`` and ``bp.rel_scan()``.

    .. caution:: It is recommended to subscribe this callback to specific plans.  It
        should not be run with just any plan (it could easily raise exceptions).

    .. rubric:: Basic example
    .. code-block::
        :linenos:

        from bluesky import plans as bp
        from bluesky import preprocessors as bpp

        signal_stats = SignalStatsCallback()

        def my_plan(detectors, mover, rel_start, rel_stop, points, md={}):

            @bpp.subs_decorator(signal_stats.receiver)  # collect the data
            def _inner():
                yield from bp.rel_scan(detectors, mover, rel_start, rel_end, points, md)

            yield from _inner()  # run the scan
            signal_stats.report()  # print the statistics

    .. rubric:: Public API
    .. autosummary::

        ~receiver
        ~report
        ~data_stream
        ~stop_report

    .. rubric:: Internal API
    .. autosummary::

        ~clear
        ~descriptor
        ~event
        ~start
        ~stop
        ~_scanning
        ~_registers
    """

    data_stream: str = "primary"
    """RunEngine document with signals to to watch."""

    stop_report: bool = True
    """If ``True`` (default), call the ``report()`` method when a ``stop`` document is received."""

    _scanning: bool = False
    """Is a run *in progress*?"""

    _registers: dict = {}
    """Dictionary (keyed on Signal name) of ``SummationRegister()`` objects."""

    # TODO: What happens when the run is paused?

    def __repr__(self):
        if "_motor" not in dir(self):  # not initialized
            self.clear()
        args = f"motor={self._motor!r},  detectors={self._detectors!r}"
        return f"{self.__class__.__name__}({args})"

    def clear(self):
        """Clear the internal memory for the next run."""
        self._scanning = False
        self._detectors = []
        self._motor = ""
        self._registers = {}
        self._descriptor_uid = None
        self._x_name = None
        self._y_names = []

    def descriptor(self, doc):
        """Receives 'descriptor' documents from the RunEngine."""
        if not self._scanning:
            return
        if doc["name"] != self.data_stream:
            return

        # Remember now, to match with later events.
        self._descriptor_uid = doc["uid"]

        # Pick the first motor signal.
        self._x_name = doc["hints"][self._motor]["fields"][0]
        # Get the signals for each detector object.s
        for d in self._detectors:
            self._y_names += doc["hints"][d]["fields"]

        # Keep statistics for each of the Y signals (vs. the one X signal).
        self._registers = {y: pysumreg.SummationRegisters() for y in self._y_names}

    def event(self, doc):
        """Receives 'event' documents from the RunEngine."""
        if not self._scanning:
            return
        if doc["descriptor"] != self._descriptor_uid:
            return

        # Collect the data for the signals.
        x = doc["data"][self._x_name]
        for yname in self._y_names:
            self._registers[yname].add(x, doc["data"][yname])

    def receiver(self, key, document):
        """Client method used to subscribe to the RunEngine."""
        handlers = "start stop descriptor event".split()
        if key in handlers:
            getattr(self, key)(document)
        else:
            logger.debug("%s: unhandled document type: %s", self.__class__.__name__, key)

    def report(self):
        """Print a table with the collected statistics for each signal."""
        if len(self._registers) == 0:
            return
        keys = "n centroid sigma x_at_max_y max_y min_y mean_y stddev_y".split()
        table = pyRestTable.Table()
        if len(keys) <= len(self._registers):
            # statistics in the column labels
            table.labels = ["detector"] + keys
            for yname, stats in self._registers.items():
                row = [yname]
                for k in keys:
                    try:
                        v = getattr(stats, k)
                    except (ValueError, ZeroDivisionError):
                        v = 0
                    row.append(v)
                table.addRow(row)
        else:
            # signals in the column labels
            table.labels = ["statistic"] + list(self._registers)
            for k in keys:
                row = [k]
                for stats in self._registers.values():
                    try:
                        v = getattr(stats, k)
                    except (ValueError, ZeroDivisionError):
                        v = 0
                    row.append(v)
                table.addRow(row)
        print(f"Motor: {self._x_name}")
        print(table)

    def start(self, doc):
        """Receives 'start' documents from the RunEngine."""
        self.clear()
        self._scanning = True
        # These command arguments might each have many signals.
        self._detectors = doc["detectors"]
        self._motor = doc["motors"][0]  # just keep the first one

    def stop(self, doc):
        """Receives 'stop' documents from the RunEngine."""
        if not self._scanning:
            return
        self._scanning = False
        if self.stop_report:
            self.report()
