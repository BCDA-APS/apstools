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
from typing import Any, Dict, Generator, List, Optional, Tuple, Union

import numpy as np
import pyRestTable
from scipy.optimize import curve_fit
from scipy.special import erf

from bluesky import plan_stubs as bps
from bluesky import plans as bp
from bluesky import preprocessors as bpp
from bluesky.callbacks import BestEffortCallback
from bluesky.callbacks.fitting import PeakStats
from ophyd import Component
from ophyd import Device
from ophyd import Signal
from ophyd.scaler import ScalerCH
from ophyd.scaler import ScalerChannel

from .. import utils
from .doc_run import write_stream

logger = logging.getLogger(__name__)
MAIN = sys.modules["__main__"]


def lineup(
    detectors: Union[Signal, List[Signal]],
    axis: Signal,
    minus: float,
    plus: float,
    npts: int,
    time_s: float = 0.1,
    peak_factor: float = 4,
    width_factor: float = 0.8,
    feature: str = "cen",
    rescan: bool = True,
    bec: Optional[BestEffortCallback] = None,
    md: Optional[Dict[str, Any]] = None,
) -> Generator[None, None, None]:
    """
    (use ``lineup2()`` now) Lineup and center a given axis, relative to current position.

    If first run identifies a peak, makes a second run to fine tune the result.

    ..caution:: ``lineup()`` does not work in the queueserver.  Use
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

    def peak_analysis() -> Generator[None, None, None]:
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

            if aligned:
                yield from bps.mv(axis, final)
                logger.info("moved %s to %f", axis.name, final)
            else:
                logger.error("failed to find peak")
                final = old_position

            if rescan and aligned:
                yield from peak_analysis()
            else:
                yield from bps.null()

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


def edge_align(
    detectors: Union[Signal, List[Signal]],
    mover: Signal,
    start: float,
    end: float,
    points: int,
    cat: Optional[str] = None,
    md: Optional[Dict[str, Any]] = None,
) -> Generator[None, None, None]:
    """
    Align to an edge using an error function fit.

    .. index:: Bluesky Plan; edge_align

    PARAMETERS

    detectors
        *[object]* or *object* : Instance(s) of ophyd.Signal (or subclass such
        as ophyd.scaler.ScalerChannel) dependent measurement to be maximized.
        If a list, the first signal in the list will be used.

    mover
        movable *object* : instance of ophyd.Signal (or subclass such as
        EpicsMotor) independent axis to use for alignment

    start
        *float* : first point of scan

    end
        *float* : last point of scan

    points
        *int* : number of data points in the scan

    cat
        *str* : category name for the scan (default: None)

    md
        *dict* : metadata dictionary (default: {})
    """
    if not isinstance(detectors, (tuple, list)):
        detectors = [detectors]
    det0 = detectors[0]  # TODO : askpete # noqa F841

    def guess_erf_params(x_data: np.ndarray, y_data: np.ndarray) -> Tuple[float, float, float, float]:
        """
        Guess initial parameters for error function fit.

        Args:
            x_data: Array of x values
            y_data: Array of y values

        Returns:
            Tuple of (low, high, width, midpoint) parameters
        """
        low = np.min(y_data)
        high = np.max(y_data)
        width = (end - start) / 10
        midpoint = (end + start) / 2
        return low, high, width, midpoint

    def erf_model(x: np.ndarray, low: float, high: float, width: float, midpoint: float) -> np.ndarray:
        """
        Error function model for edge fitting.

        Args:
            x: Array of x values
            low: Lower asymptote
            high: Upper asymptote
            width: Width of the transition
            midpoint: Center of the transition

        Returns:
            Array of y values
        """
        return low + (high - low) * (1 + erf((x - midpoint) / width)) / 2

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


def lineup2(
    detectors: Union[Signal, List[Signal]],
    mover: Signal,
    rel_start: float,
    rel_end: float,
    points: int,
    peak_factor: float = 1.5,
    width_factor: float = 0.8,
    feature: str = "centroid",
    nscans: int = 2,
    signal_stats: Optional[Any] = None,
    reporting: Optional[Any] = None,
    md: Optional[Dict[str, Any]] = None,
) -> Generator[None, None, None]:
    """
    Lineup and center a given axis, relative to current position.

    .. index:: Bluesky Plan; lineup2

    PARAMETERS

    detectors
        *[object]* or *object* : Instance(s) of ophyd.Signal (or subclass such
        as ophyd.scaler.ScalerChannel) dependent measurement to be maximized.
        If a list, the first signal in the list will be used.

    mover
        movable *object* : instance of ophyd.Signal (or subclass such as
        EpicsMotor) independent axis to use for alignment

    rel_start
        *float* : first point of scan at this offset from starting position

    rel_end
        *float* : last point of scan at this offset from starting position

    points
        *int* : number of data points in the scan

    peak_factor
        *float* : peak maximum must be greater than ``peak_factor*minimum``
        (default: 1.5)

    width_factor
        *float* : fwhm must be less than ``width_factor*plot_range`` (default:
        0.8)

    feature
        *str* : One of the parameters returned by BestEffortCallback peak stats.
        (``cen``, ``com``, ``max``, ``min``) (default: ``centroid``)

    nscans
        *int* : number of scans to perform (default: 2)

    signal_stats
        *object* : Instance of BestEffortCallback (default: None)

    reporting
        *object* : Instance of LiveTable or other reporting callback (default: None)

    md
        *dict* : metadata dictionary (default: {})
    """
    if not isinstance(detectors, (tuple, list)):
        detectors = [detectors]
    det0 = detectors[0]

    def find_peak_position() -> Generator[None, None, Optional[float]]:
        """
        Find the peak position in the current scan.

        Returns:
            The peak position if found, None otherwise.
        """
        if det0.name not in signal_stats.peaks[feature]:
            logger.error(
                "No statistical analysis of scan peak for feature '%s'!"
                "  (signal_stats.peaks=%s, signal_stats=%s)",
                feature,
                signal_stats.peaks,
                signal_stats,
            )
            yield from bps.null()
            return None

        stats = signal_stats.peaks
        if not strong_peak(stats):
            logger.error("no clear peak")
            return None
        if too_wide(stats):
            logger.error("FWHM too large")
            return None

        return stats[feature][det0.name]

    def strong_peak(stats: Any) -> bool:
        """
        Check if a strong peak is detected.

        Args:
            stats: Peak statistics from BestEffortCallback

        Returns:
            True if a strong peak is detected, False otherwise
        """
        hi = stats["max"][det0.name][-1]
        lo = stats["min"][det0.name][-1]
        return hi > peak_factor * lo

    def too_wide(stats: Any) -> bool:
        """
        Check if the peak is too wide.

        Args:
            stats: Peak statistics from BestEffortCallback

        Returns:
            True if the peak is too wide, False otherwise
        """
        ps = list(signal_stats._peak_stats.values())[0][det0.name]
        x_range = abs(max(ps.x_data) - min(ps.x_data))
        fwhm = stats["fwhm"][det0.name]
        return fwhm > width_factor * x_range

    @bpp.subs_decorator(signal_stats.receiver)
    def _inner() -> Generator[None, None, None]:
        """
        Inner function to perform the scan and analysis.
        """
        # ... rest of the function implementation ...


class TuneAxis:
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

    Also see the jupyter notebook tited **Demonstrate TuneAxis()**
    in the :ref:`examples` section.

    .. autosummary::

       ~tune
       ~multi_pass_tune
       ~peak_detected

    SEE ALSO

    .. autosummary::

       ~tune_axes

    """

    _peak_choices_: List[str] = "cen com".split()

    def __init__(
        self,
        signals: Union[Signal, List[Signal]],
        axis: Signal,
        signal_name: Optional[str] = None,
    ) -> None:
        """
        Initialize the TuneAxis object.

        Args:
            signals: Signal or list of signals to monitor
            axis: Axis to tune
            signal_name: Name of the signal to use (default: None)
        """
        if not isinstance(signals, (tuple, list)):
            signals = [signals]
        self.signals = signals
        self.axis = axis
        self.signal_name = signal_name or signals[0].name
        self.peaks = PeakStats()

    def tune(
        self,
        width: Optional[float] = None,
        num: Optional[int] = None,
        peak_factor: Optional[float] = None,
        md: Optional[Dict[str, Any]] = None,
    ) -> Generator[None, None, None]:
        """
        Tune the axis.

        Args:
            width: Width of the scan range
            num: Number of points in the scan
            peak_factor: Factor for peak detection
            md: Metadata dictionary
        """
        # ... rest of the method implementation ...

    def multi_pass_tune(
        self,
        width: Optional[float] = None,
        step_factor: Optional[float] = None,
        num: Optional[int] = None,
        pass_max: Optional[int] = None,
        peak_factor: Optional[float] = None,
        snake: Optional[bool] = None,
        md: Optional[Dict[str, Any]] = None,
    ) -> Generator[None, None, None]:
        """
        Perform multiple passes of tuning.

        Args:
            width: Width of the scan range
            step_factor: Factor to reduce step size by
            num: Number of points in the scan
            pass_max: Maximum number of passes
            peak_factor: Factor for peak detection
            snake: Whether to alternate scan direction
            md: Metadata dictionary
        """
        # ... rest of the method implementation ...

    def multi_pass_tune_summary(self) -> None:
        """
        Print a summary of the multi-pass tuning results.
        """
        # ... rest of the method implementation ...

    def peak_detected(self, peak_factor: Optional[float] = None) -> bool:
        """
        Check if a peak was detected.

        Args:
            peak_factor: Factor for peak detection

        Returns:
            True if a peak was detected, False otherwise
        """
        # ... rest of the method implementation ...


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
