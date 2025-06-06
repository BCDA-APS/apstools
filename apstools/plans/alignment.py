"""
Alignment plans
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~lineup
   ~lineup2
   ~tune_axes
   ~TuneAxis
   ~TuneResults
"""

import datetime
import logging
import sys

import numpy as np
import pyRestTable
from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky import preprocessors as bpp
from bluesky.callbacks.fitting import PeakStats
from bluesky.utils import plan
from deprecated.sphinx import deprecated
from deprecated.sphinx import versionadded
from deprecated.sphinx import versionchanged
from ophyd import Component
from ophyd import Device
from ophyd import Signal
from ophyd.scaler import ScalerCH
from ophyd.scaler import ScalerChannel
from scipy.optimize import curve_fit
from scipy.special import erf

from .. import utils
from .doc_run import write_stream

logger = logging.getLogger(__name__)
MAIN = sys.modules["__main__"]


@deprecated(version="1.7.2", reason="use lineup2()")
@plan
def lineup(
    # fmt: off
    detectors,
    axis,
    minus,
    plus,
    npts,
    time_s=0.1,
    peak_factor=4,
    width_factor=0.8,
    feature="cen",
    rescan=True,
    bec=None,
    md=None,
    # fmt: on
):
    """
    **Deprecated** Lineup and center a given axis, relative to current position.

    If first run identifies a peak, makes a second run to fine tune the result.

    .. caution:: ``lineup()`` does not work in the queueserver.  Use
        :func:`~apstools.plans.alignment.lineup2()` instead.

    .. index:: Bluesky Plan; lineup

    PARAMETERS

    detectors
        *[object]* or *object* : Instance(s) of ophyd.Signal (or subclass such
        as ophyd.scaler.ScalerChannel) dependent measurement to be maximized.
        If a list, the first signal in the list will be used.

    axis
        movable *object* : instance of ophyd.Signal (or subclass such as
        EpicsMotor) independent axis to use for alignment

    minus
        *float* : first point of scan at this offset from starting position

    plus
        *float* : last point of scan at this offset from starting position

    npts
        *int* : number of data points in the scan

    time_s
        *float* : Count time per step (if detectors[0] is ScalerChannel object),
        other object types not yet supported. (default: 0.1)

    peak_factor
        *float* : peak maximum must be greater than ``peak_factor*minimum``
        (default: 4)

    width_factor
        *float* : fwhm must be less than ``width_factor*plot_range`` (default:
        0.8)

    feature
        *str* : One of the parameters returned by BestEffortCallback peak stats.
        (``cen``, ``com``, ``max``, ``min``) (default: ``cen``)

    rescan
        *bool* : If first scan indicates a peak, should a second scan refine the
        result? (default: ``True``)

    bec
        *object* : Instance of
        ``bluesky.callbacks.best_effort.BestEffortCallback``. (default:
        ``None``, meaning look for it from global namespace)

    EXAMPLE::

        RE(lineup(diode, foemirror.theta, -30, 30, 30, 1.0))
    """
    if bec is None:
        if "bec" in dir(MAIN):
            # get from __main__ namespace
            bec = getattr(MAIN, "bec")
        else:
            raise ValueError("Cannot find BestEffortCallback() instance.")
    bec.enable_plots()

    if not isinstance(detectors, (tuple, list)):
        detectors = [detectors]
    det0 = detectors[0]
    logger.info("Using detector '%s' for lineup()", det0.name)

    # first, determine if det0 is part of a ScalerCH device
    scaler = None
    obj = det0.parent
    if isinstance(det0.parent, ScalerChannel):
        if hasattr(obj, "parent") and obj.parent is not None:
            obj = obj.parent
            if hasattr(obj, "parent") and isinstance(obj.parent, ScalerCH):
                scaler = obj.parent

    if scaler is not None:
        old_sigs = scaler.stage_sigs
        scaler.stage_sigs["preset_time"] = time_s
        scaler.select_channels([det0.name])

    if hasattr(axis, "position"):
        old_position = axis.position
    else:
        old_position = axis.get()

    def peak_analysis():
        aligned = False

        if det0.name not in bec.peaks[feature]:
            logger.error(
                "No statistical analysis of scan peak for feature '%s'!" "  (bec.peaks=%s, bec=%s)",
                feature,
                bec.peaks,
                bec,
            )
            yield from bps.null()
        else:
            table = pyRestTable.Table()
            table.labels = ("key", "value")
            table.addRow(("axis", axis.name))
            table.addRow(("detector", det0.name))
            table.addRow(("starting position", old_position))
            for key in bec.peaks.ATTRS:
                target = bec.peaks[key][det0.name]
                if isinstance(target, tuple):
                    target = target[0]
                table.addRow((key, target))
            logger.info(f"alignment scan results:\n{table}")

            lo = bec.peaks["min"][det0.name][-1]  # [-1] means detector
            hi = bec.peaks["max"][det0.name][-1]  # [0] means axis
            fwhm = bec.peaks["fwhm"][det0.name]
            final = bec.peaks["cen"][det0.name]

            # local PeakStats object of our plot of det0 .v x
            ps = list(bec._peak_stats.values())[0][det0.name]
            # get the X data range as received by PeakStats
            x_range = abs(max(ps.x_data) - min(ps.x_data))

            if final is None:
                logger.error("centroid is None")
                final = old_position
            elif fwhm is None:
                logger.error("FWHM is None")
                final = old_position
            elif hi < peak_factor * lo:
                logger.error("no clear peak: %f < %f*%f", hi, peak_factor, lo)
                final = old_position
            elif fwhm > width_factor * x_range:
                logger.error(
                    "FWHM too large: %f > %f*%f",
                    fwhm,
                    width_factor,
                    x_range,
                )
                final = old_position
            else:
                aligned = True

            logger.info(
                "moving %s to %f  (aligned: %s)",
                axis.name,
                final,
                str(aligned),
            )
            yield from bps.mv(axis, final)

        # too sneaky?  We're modifying this structure locally
        bec.peaks.aligned = aligned
        bec.peaks.ATTRS = ("com", "cen", "max", "min", "fwhm")

    _md = dict(purpose="alignment")
    _md.update(md or {})
    yield from bp.rel_scan([det0], axis, minus, plus, npts, md=_md)
    yield from peak_analysis()

    if bec.peaks.aligned and rescan:
        # again, tweak axis to maximize
        _md["purpose"] = "alignment - fine"
        fwhm = bec.peaks["fwhm"][det0.name]
        yield from bp.rel_scan([det0], axis, -fwhm, fwhm, npts, md=_md)
        yield from peak_analysis()

    if scaler is not None:
        scaler.select_channels()
        scaler.stage_sigs = old_sigs


@plan
def edge_align(detectors, mover, start, end, points, cat=None, md={}):
    """
    Align to the edge given mover & detector data, relative to absolute position.

    This plan can be used in the queueserver, Jupyter notebooks, and IPython
    consoles.

    PARAMETERS
    ----------
    detectors *Readable* or [*Readable*]:
        Detector object or list of detector objects (each is a Device or
        Signal).

    mover *Movable*:
        Mover object, such as motor or other positioner.

    start *float*:
        Starting point for the scan. This is an absolute motor location.

    end *float*:
        Ending point for the scan. This is an absolute motor location.

    points *int*:
        Number of points in the scan.

    cat *databroker.temp().v2*:
        Catalog where bluesky data is saved and can be retrieved from.

    md *dict*:
        User-supplied metadata for this scan.
    """

    def guess_erf_params(x_data, y_data):
        """
        Provide an initial guess for the parameters of an error function.

        Parameters
        ----------
        x_data : A numpy array of the values on the x_axis
        y_data : A numpy array of the values on the y_axis

        Returns
        -------
        guess : dict
            A dictionary containing the guessed parameters 'low_y_data', 'high_y_data', 'width', and 'midpoint'.
        """

        # Sort data to make finding the mid-point easier and to assist in other estimations
        y_data_sorted = np.sort(y_data)
        x_data_sorted = np.sort(x_data)

        # Estimate low and high as the first and last elements (assuming sorted data)
        low_y_data = np.min(y_data_sorted)
        high_y_data = np.max(y_data_sorted)

        low_x_data = np.min(x_data_sorted)
        high_x_data = np.max(x_data_sorted)

        # Estimate width as a fraction of the range. This is very arbitrary and might need tuning!
        # This is a guess and might need adjustment based on your data's characteristics.
        width = (high_x_data - low_x_data) / 10

        # Estimate the midpoint of the x values
        midpoint = x_data[int(len(x_data) / 2)]

        return [low_y_data, high_y_data, width, midpoint]

    def erf_model(x, low, high, width, midpoint):
        """
        Create error function for fitting and simulation

        Parameters
        ----------
        x		:	input upon which error function is evaluated
        low		: 	min value of error function
        high	: 	max value of error function
        width  	:	"spread" of error function transition region
        midpoint:	location of error function's "center"
        """
        return (high - low) * 0.5 * (1 - erf((x - midpoint) / width)) + low

    if not isinstance(detectors, (tuple, list)):
        detectors = [detectors]

    _md = dict(purpose="edge_align")
    _md.update(md or {})

    uid = yield from bp.scan(detectors, mover, start, end, points, md=_md)
    cat = cat or utils.getCatalog()
    run = cat[uid]  # return uids
    ds = run.primary.read()

    x = ds["mover"]
    y = ds["noisy"]

    try:
        initial_guess = guess_erf_params(x, y)
        popt, pcov = curve_fit(erf_model, x, y, p0=initial_guess)
        if pcov[3, 3] != np.inf:
            print("Significant signal change detected; motor moving to detected edge.")
            yield from bps.mv(mover, popt[3])
        else:
            raise Exception
    except Exception as reason:
        print(f"reason: {reason}")
        print("No significant signal change detected; motor movement skipped.")


@versionchanged(version="1.7.2", reason="Changed from PySumReg to numpy")
@versionadded(version="1.6.18")
@plan
def lineup2(
    # fmt: off
    detectors,
    mover,
    rel_start,
    rel_end,
    points,
    peak_factor=1.5,
    width_factor=0.8,
    feature="centroid",
    nscans=2,
    signal_stats=None,
    reporting=None,
    md={},
    # fmt: on
):
    """
    Lineup and center a given mover, relative to the current position.

    Step scan ``mover`` and measure ``detectors`` at each step. Peak analysis is
    based on data collected during the scan for the **first** detector (in the
    list of ``detectors``) *vs.* ``mover``.  If a peak is detected, move the
    ``mover`` to the feature position (default is ``"centroid"``). If
    ``nscans>1``, adjust the scan range based on the apparent FWHM and rescan.
    At most, a total of ``nscans`` will be run.

    If unable to identify a peak, ``lineup2()`` returns ``mover`` to its
    original position and returns (no more rescans).  If ``lineup2()`` fails to
    identify a peak that you can observe, consider re-running with increased
    ``points``, changed range(``rel_start`` and ``rel_end``), and/or changed
    terms (``peak_factor`` and ``width_factor``).

    Increase ``nscans`` for additional fine-tuning of the ``centroid`` and
    ``fwhm`` parameters.  It is probably not necessary to set ``nscans>5``.

    .. index:: Bluesky Plan; lineup2; lineup

    This plan can be used in the queueserver, Jupyter notebooks, and IPython
    consoles.  It does not require the bluesky BestEffortCallback.  Instead, it
    uses *numpy*  [#numpy]_ to compute statistics for each signal in a 1-D
    scan.

    .. rubric::  PARAMETERS

    detectors *Readable* or [*Readable*]:
        Detector object or list of detector objects (each is a Device or
        Signal). If a list, the first Signal will be used for alignment.

    mover *Movable*:
        Mover object, such as motor or other positioner.

    rel_start *float*:
        Starting point for the scan, relative to the current mover position.

    rel_end *float*:
        Ending point for the scan, relative to the current mover position.

    points *int*:
        Number of points in the scan.

    peak_factor *float* :
        peak maximum must be greater than ``peak_factor*minimum`` (default: 2.5)

    width_factor *float* :
        fwhm must be less than ``width_factor*plot_range`` (default: 0.8)

    feature *str*:
        Use this statistical measure (default: centroid) to set the mover
        position after a peak has been found.  Must be one of these values:

        ==========  ====================
        feature     description
        ==========  ====================
        centroid    center of mass
        x_at_max_y  x location of y maximum
        x_at_min_y  x location of y minimum
        ==========  ====================

        Statistical analysis provided by *numpy*.  [#numpy]_
        (Previous versions used *PySumReg*.  [#pysumreg]_)

        .. [#numpy] https://numpy.org/
        .. [#pysumreg] https://prjemian.github.io/pysumreg/latest/

    nscans *int*:
        Number of scans.  (default: 2)  Scanning will stop if any scan cannot
        find a peak.

    signal_stats *object*:
        Caller could provide an object of
        :class:`~apstools.callbacks.scan_signal_statistics.SignalStatsCallback`.

        When ``signal_stats`` is not provided, this function will search for the
        ``signal_stats`` signal in the global (``__main__``) namespace. If not
        still found, a new ``signal_stats`` will be created and then added to
        the global namespace.

        Results of the analysis are available in ``signal_stats.analysis``.  The
        data used for the analysis are available in ``signal_stats._data``. The
        PySumReg analysis remains available (for now)
        in ``signal_stats._registers``.

    md *dict*:
        User-supplied metadata for this scan.

    ----

    In addition to the many keys provided in `signal_stats.analysis` by
    :class:`~apstools.callbacks.scan_signal_statistics.SignalStatsCallback`,
    this plan adds two keys as follows:

    .. rubric::  Keys added to signal_stats.analysis dictionary

    success : bool
        Did ``lineup2()`` identify a peak and set the mover to its value?

    reason : [str]
        If ``success=False``, this is a list of the reasons why ``lineup2()``
        did not identify a peak.
    """
    from ..callbacks import SignalStatsCallback

    if not isinstance(detectors, (tuple, list)):
        detectors = [detectors]

    _md = dict(purpose="alignment")
    _md.update(md or {})

    # Do not move the positioner outside the limits of the first scan.
    try:
        m_pos = mover.position
    except AttributeError:
        m_pos = mover.get()
    m_lo = m_pos + rel_start
    m_hi = m_pos + rel_end

    if signal_stats is None:
        # Print report() when stop document is received.
        if "signal_stats" in dir(MAIN):
            # get from __main__ namespace
            signal_stats = getattr(MAIN, "signal_stats")
        else:
            signal_stats = SignalStatsCallback()
            # Add signal_stats to __main__ namespace.  Users have requested
            # a way to determine if a lineup failed and why.
            setattr(MAIN, "signal_stats", signal_stats)
        signal_stats.reporting = True if reporting is None else reporting
    else:
        # Do not print report() when stop document is received.
        signal_stats.reporting = False if reporting is None else reporting

    # Allow for feature to be defined using a name from PeakStats.
    xref_PeakStats = {
        "com": "centroid",
        "cen": "x_at_max_y",
        "max": "x_at_max_y",
        "min": "x_at_min_y",
    }
    # translate from PeakStats feature to SignalStats
    feature = xref_PeakStats.get(feature, feature)

    def find_peak_position():
        """Return the X value of the specified 'feature'."""
        stats = signal_stats.analysis
        logging.debug("stats: %s", stats)
        peak_is_strong = strong_peak(stats)
        peak_too_wide = too_wide(stats)
        peak_width_zero = stats.fwhm == 0
        peak_sigma_zero = stats.get("sigma", 0) == 0
        findings = [
            peak_is_strong,
            not peak_too_wide,
            not peak_width_zero,
            not peak_sigma_zero,
        ]
        if all(findings):
            stats["success"] = True
            return getattr(stats, feature)

        # Save these into stats for the caller to find.
        stats["success"] = False
        stats["reasons"] = []
        if not peak_is_strong:
            stats["reasons"].append("No strong peak found.")
        if peak_too_wide:
            stats["reasons"].append("Peak is too wide.")
        if peak_width_zero:
            stats["reasons"].append("FWHM is zero.")
        if peak_sigma_zero:
            stats["reasons"].append("Computed peak sigma is zero.")
        print(" ".join(stats["reasons"]))
        logger.debug("No peak found.  Reasons: %s", stats["reasons"])
        logger.debug("stats: %s", stats)

    def strong_peak(stats) -> bool:
        """Determine if the peak is strong."""
        try:
            denominator = stats.mean_y - stats.min_y
            if denominator == 0:
                raise ZeroDivisionError()
            return abs((stats.max_y - stats.min_y) / denominator) > peak_factor
        except (AttributeError, ZeroDivisionError):
            return False

    def too_wide(stats):
        """Does the measured peak width fill the full range of X?"""
        fallback_errors = (
            AttributeError,  # no statistics available
            ValueError,  # math domain error: variance<0 (noise, no clear peak)
            ZeroDivisionError,  # not enough samples
        )
        try:
            return stats.fwhm > width_factor * (stats.max_x - stats.min_x)
        except fallback_errors as reason:
            logger.warning("Cannot detect width: %s", reason)
            logger.debug("Statistics: %s", stats)
            return True

    if "plan_name" not in _md:
        _md["plan_name"] = "lineup2"

    @bpp.subs_decorator(signal_stats.receiver)
    def _inner():
        """Run the scan, collecting statistics at each step."""
        # TODO: save signal stats into separate stream
        yield from bp.rel_scan(detectors, mover, rel_start, rel_end, points, md=_md)

    while nscans > 0:  # allow for repeated scans
        yield from _inner()  # Run the scan.
        nscans -= 1

        target = find_peak_position()
        if target is None:
            nscans = 0  # Nothing found, no point scanning again.
            yield from bps.mv(mover, m_pos)  # back to starting position
            logger.debug("Moved %s to %s: %f", mover.name, "original position", m_pos)
        else:
            # Maintain absolute range: m_lo <= target <= m_hi
            target = min(max(m_lo, target), m_hi)
            yield from bps.mv(mover, target)  # Move to the feature position.
            logger.info("Moved %s to %s: %f", mover.name, feature, target)

            if nscans > 0:
                # move the end points for the next scan
                offset = 2 * signal_stats.analysis.fwhm
                # Can't move outside absolute range of m_lo..m_hi
                rel_start = max(m_lo - target, -offset)
                rel_end = min(m_hi - target, offset)

    if signal_stats.reporting:  # Final report
        signal_stats.report()


class TuneAxis(object):
    """
    tune an axis with a signal

    .. index:: Bluesky Device; TuneAxis

    This class provides a tuning object so that a Device or other entity
    may gain its own tuning process, keeping track of the particulars
    needed to tune this device again.  For example, one could add
    a tuner to a motor stage::

        motor = EpicsMotor("xxx:motor", "motor")
        motor.tuner = TuneAxis([det], motor)

    Then the ``motor`` could be tuned individually::

        RE(motor.tuner.tune(md={"activity": "tuning"}))

    or the :meth:`tune()` could be part of a plan with other steps.

    Example::

        tuner = TuneAxis([det], axis)
        live_table = LiveTable(["axis", "det"])
        RE(tuner.multi_pass_tune(width=2, num=9), live_table)
        RE(tuner.tune(width=0.05, num=9), live_table)

    Also see the :doc:`The TuneAxis() plan </examples/pl_tuneaxis>` (jupyter
    notebook).

    .. autosummary::

       ~tune
       ~multi_pass_tune
       ~peak_detected

    SEE ALSO

    .. autosummary::

       ~tune_axes

    """

    _peak_choices_ = "cen com".split()

    def __init__(self, signals, axis, signal_name=None):
        self.signals = signals
        self.signal_name = signal_name or signals[0].name
        self.axis = axis
        self.tune_ok = False
        self.peaks = None
        self.peak_choice = self._peak_choices_[0]
        self.center = None
        self.stats = []

        # defaults
        self.width = 1
        self.num = 10
        self.step_factor = 4
        self.peak_factor = 4
        self.pass_max = 4
        self.snake = True

    def tune(self, width=None, num=None, peak_factor=None, md=None):
        """
        Bluesky plan to execute one pass through the current scan range

        .. index:: Bluesky Plan; TuneAxis.tune

        Scan self.axis centered about current position from
        ``-width/2`` to ``+width/2`` with ``num`` observations.
        If a peak was detected (default check is that max >= 4*min),
        then set ``self.tune_ok = True``.

        PARAMETERS

        width
            *float* :
            width of the tuning scan in the units of ``self.axis``
            Default value in ``self.width`` (initially 1)
        num
            *int* :
            number of steps
            Default value in ``self.num`` (initially 10)
        md
            *dict* :
            (optional)
            metadata
        """
        width = width or self.width
        num = num or self.num
        peak_factor = peak_factor or self.peak_factor

        if self.peak_choice not in self._peak_choices_:
            msg = "peak_choice must be one of {}, geave {}"
            msg = msg.format(self._peak_choices_, self.peak_choice)
            raise ValueError(msg)

        initial_position = self.axis.position
        # final_position = initial_position       # unless tuned
        start = initial_position - width / 2
        finish = initial_position + width / 2
        self.tune_ok = False

        tune_md = dict(
            width=width,
            initial_position=self.axis.position,
            time_iso8601=str(datetime.datetime.now()),
        )
        _md = {
            "tune_md": tune_md,
            "plan_name": self.__class__.__name__ + ".tune",
            "tune_parameters": dict(
                num=num,
                width=width,
                initial_position=self.axis.position,
                peak_choice=self.peak_choice,
                x_axis=self.axis.name,
                y_axis=self.signal_name,
            ),
            "motors": (self.axis.name,),
            "detectors": (self.signal_name,),
            "hints": dict(dimensions=[([self.axis.name], "primary")]),
        }
        _md.update(md or {})
        if "pass_max" not in _md:
            self.stats = []
        self.peaks = PeakStats(x=self.axis.name, y=self.signal_name)

        @bpp.subs_decorator(self.peaks)
        def _scan(md=None):
            yield from bps.open_run(md)

            position_list = np.linspace(start, finish, num)
            # fmt: off
            signal_list = list(self.signals)
            signal_list += [self.axis]
            # fmt: on
            for pos in position_list:
                yield from bps.mv(self.axis, pos)
                yield from bps.trigger_and_read(signal_list)

            final_position = initial_position
            if self.peak_detected(peak_factor=peak_factor):
                self.tune_ok = True
                if self.peak_choice == "cen":
                    final_position = self.peaks.cen
                elif self.peak_choice == "com":
                    final_position = self.peaks.com
                else:
                    final_position = None
                self.center = final_position

            # add stream with results
            # yield from add_results_stream()
            stream_name = "PeakStats"
            results = TuneResults(name=stream_name)

            results.tune_ok.put(self.tune_ok)
            results.center.put(self.center)
            results.final_position.put(final_position)
            results.initial_position.put(initial_position)
            results.set_stats(self.peaks)
            self.stats.append(results)

            if results.tune_ok.get():
                try:
                    yield from write_stream(results, label=stream_name)
                except ValueError as ex:
                    separator = " " * 8 + "-" * 12
                    print(separator)
                    print(f"Error saving stream {stream_name}:\n{ex}")
                    print(separator)

            yield from bps.mv(self.axis, final_position)
            yield from bps.close_run()

            results.report(stream_name)

        return (yield from _scan(md=_md))

    def multi_pass_tune(
        self,
        width=None,
        step_factor=None,
        num=None,
        pass_max=None,
        peak_factor=None,
        snake=None,
        md=None,
    ):
        """
        Bluesky plan for tuning this axis with this signal

        Execute multiple passes to refine the centroid determination.
        Each subsequent pass will reduce the width of scan by ``step_factor``.
        If ``snake=True`` then the scan direction will reverse with
        each subsequent pass.

        PARAMETERS

        width
            *float* :
            width of the tuning scan in the units of ``self.axis``
            Default value in ``self.width`` (initially 1)
        num
            *int* :
            number of steps
            Default value in ``self.num`` (initially 10)
        step_factor
            *float* :
            This reduces the width of the next tuning scan by the given factor.
            Default value in ``self.step_factor`` (initially 4)
        pass_max
            *int* :
            Maximum number of passes to be executed (avoids runaway
            scans when a centroid is not found).
            Default value in ``self.pass_max`` (initially 4)
        peak_factor
            *float* :
            peak maximum must be greater than ``peak_factor*minimum``
            (default: 4)
        snake
            *bool* :
            If ``True``, reverse scan direction on next pass.
            Default value in ``self.snake`` (initially True)
        md
            *dict* :
            (optional)
            metadata
        """
        width = width or self.width
        num = num or self.num
        step_factor = step_factor or self.step_factor
        snake = snake or self.snake
        pass_max = pass_max or self.pass_max
        peak_factor = peak_factor or self.peak_factor

        self.stats = []

        def _scan(width=1, step_factor=10, num=10, snake=True):
            for _pass_number in range(pass_max):
                logger.info("Multipass tune %d of %d", _pass_number + 1, pass_max)
                _md = {
                    "pass": _pass_number + 1,
                    "pass_max": pass_max,
                    "plan_name": f"{self.__class__.__name__}.multi_pass_tune",
                }
                _md.update(md or {})

                yield from self.tune(width=width, num=num, peak_factor=peak_factor, md=_md)

                if not self.tune_ok:
                    return
                if width > 0:
                    sign = 1
                else:
                    sign = -1
                width = sign * 2 * self.stats[-1].fwhm.get()
                if snake:
                    width *= -1

        return (yield from _scan(width=width, step_factor=step_factor, num=num, snake=snake))

    def multi_pass_tune_summary(self):
        t = pyRestTable.Table()
        t.labels = "pass Ok? center width max.X max.Y".split()
        for i, stat in enumerate(self.stats):
            row = [
                i + 1,
            ]
            row.append(stat.tune_ok.get())
            row.append(stat.cen.get())
            row.append(stat.fwhm.get())
            x, y = stat.max.get()
            row += [x, y]
            t.addRow(row)
        return t

    def peak_detected(self, peak_factor=None):
        """
        returns True if a peak was detected, otherwise False

        The default algorithm identifies a peak when the maximum
        value is four times the minimum value.  Change this routine
        by subclassing :class:`TuneAxis` and override :meth:`peak_detected`.
        """
        peak_factor = peak_factor or self.peak_factor

        if self.peaks is None:
            return False
        self.peaks.compute()
        if self.peaks.max is None:
            return False

        ymax = self.peaks.max[-1]
        ymin = self.peaks.min[-1]
        ok = ymax >= peak_factor * ymin  # this works for USAXS@APS
        if not ok:
            logger.info("ymax < ymin * %f: is it a peak?", peak_factor)
        return ok


def tune_axes(axes):
    """
    Bluesky plan to tune a list of axes in sequence.

    Expects each axis will have a ``tuner`` attribute which is an instance of
    :class:`~apstools.plans.alignment.TuneAxis()`.

    .. index:: Bluesky Plan; tune_axes

    EXAMPLE

    Sequentially, tune a list of preconfigured axes::

        RE(tune_axes([mr, m2r, ar, a2r])

    SEE ALSO

    .. autosummary::

       ~TuneAxis
    """
    for axis in axes:
        if "tuner" not in dir(axis):
            raise AttributeError(f"Did not find '{axis.name}.tuner' attribute.")
        yield from axis.tuner.tune()


class TuneResults(Device):
    """
    Provides bps.read() as a Device

    .. index:: Bluesky Device; TuneResults
    """

    tune_ok = Component(Signal)
    initial_position = Component(Signal)
    final_position = Component(Signal)
    center = Component(Signal)
    # - - - - -
    x = Component(Signal)
    y = Component(Signal)
    cen = Component(Signal)
    com = Component(Signal)
    fwhm = Component(Signal)
    min = Component(Signal)
    max = Component(Signal)
    crossings = Component(Signal)
    peakstats_attrs = "x y cen com fwhm min max crossings".split()

    def report(self, title=None):
        keys = self.peakstats_attrs + "tune_ok center initial_position final_position".split()
        t = pyRestTable.Table()
        t.addLabel("key")
        t.addLabel("result")
        for key in keys:
            v = getattr(self, key).get()
            t.addRow((key, str(v)))
        if title is not None:
            print(title)
        print(t)

    def set_stats(self, peaks):
        for key in self.peakstats_attrs:
            v = getattr(peaks, key)
            if v is None:  # None cannot be mapped into json
                v = "null"  # but "null" can replace it
            if key in ("crossings", "min", "max"):
                v = np.array(v)
            getattr(self, key).put(v)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
