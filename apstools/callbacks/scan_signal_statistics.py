"""
Collect statistics on the first detector used in 1-D scans.
===========================================================

.. autosummary::

    ~SignalStatsCallback
"""

import logging

import pyRestTable
import pysumreg  # deprecate, will remove in next major version bump

logger = logging.getLogger(__name__)
logger.info(__file__)


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
        from apstools.callbacks import SignalStatsCallback

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
        ~reporting

    .. rubric:: Internal API
    .. autosummary::

        ~clear
        ~descriptor
        ~event
        ~start
        ~stop
        ~analysis
        ~_data
        ~_scanning
        ~_registers
    """

    data_stream: str = "primary"
    """RunEngine document with signals to to watch."""

    reporting: bool = True
    """If ``True`` (default), call the ``report()`` method when a ``stop`` document is received."""

    _scanning: bool = False
    """Is a run *in progress*?"""

    _registers: dict = {}
    """
    Deprecated: Use 'analysis' instead, will remove in next major release.

    Dictionary (keyed on Signal name) of ``SummationRegister()`` objects.
    """

    _data: dict = {}
    """Arrays of x & y data"""

    analysis: object = None
    """Dictionary of statistical array analyses."""

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
        self._registers = {}  # deprecated, for removal
        self._descriptor_uid = None
        self._x_name = None
        self._y_names = []
        self._data = {}

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
        self._data[self._x_name] = []

        # Get the signals for each detector object(s)
        for d in self._detectors:
            hint = doc["hints"].get(d, {"fields": [d]})
            for y_name in hint["fields"]:
                if y_name not in self._y_names:
                    self._y_names.append(y_name)
                    self._data[y_name] = []

        # Keep statistics for each of the Y signals (vs. the one X signal).
        # deprecated, for removal
        self._registers = {y: pysumreg.SummationRegisters() for y in self._y_names}

    def event(self, doc):
        """Receives 'event' documents from the RunEngine."""
        if not self._scanning:
            return
        if doc["descriptor"] != self._descriptor_uid:
            return

        # Collect the data for the signals.
        x = doc["data"][self._x_name]
        self._data[self._x_name].append(x)

        for yname in self._y_names:
            y = doc["data"][yname]
            self._registers[yname].add(x, y)  # deprecated, for removal
            self._data[yname].append(y)

    def receiver(self, key, document):
        """Client method used to subscribe to the RunEngine."""
        handlers = "start stop descriptor event".split()
        if key in handlers:
            getattr(self, key)(document)
        else:
            logger.debug("%s: unhandled document type: %s", self.__class__.__name__, key)

    def report(self):
        """Print a table with the collected statistics for each signal."""
        if len(self._data) == 0:
            return

        x_name = self._x_name
        y_name = self._detectors[0]

        keys = """
            n centroid x_at_max_y
            fwhm variance sigma
            min_x mean_x max_x
            min_y mean_y max_y
            success reasons
        """.split()

        table = pyRestTable.Table()
        table.labels = "statistic value".split()
        table.rows = [(k, self.analysis.get(k, "--")) for k in keys if k in self.analysis]
        print(f"Motor: {x_name!r}  Detector: {y_name!r}")
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
        from ..utils.statistics import xy_statistics

        if not self._scanning:
            return
        self._scanning = False

        self.analysis = xy_statistics(
            self._data[self._x_name],
            self._data[self._y_names[0]],
        )

        if self.reporting:
            self.report()
