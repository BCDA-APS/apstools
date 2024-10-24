"""
PVPositioner that computes ``done`` as a soft signal.

.. autosummary::

   ~PVPositionerSoftDone
   ~PVPositionerSoftDoneWithStop
"""

import atexit
import logging
import math
import weakref

from ophyd import Component
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent
from ophyd import PVPositioner
from ophyd import Signal

# from ..tests import timed_pause

logger = logging.getLogger(__name__)

# Must use a data type that can be serialized as json (Python's None cannot be serialized)
# This ValueError: Cannot determine the appropriate bluesky-friendly data type for value
# None of Python type <class 'NoneType'>. Supported types include: int, float, str, and
# iterables such as list, tuple, np.ndarray, and so on.
TARGET_UNDEFINED = "undefined"


class PVPositionerSoftDone(PVPositioner):
    """
    PVPositioner that computes ``done`` as a soft signal.

    PARAMETERS

    prefix : str, optional
        The device prefix used for all sub-positioners.
        This is optional as it
        may be desirable to specify full PV names for PVPositioners.
    readback_pv : str, optional
        PV prefix of the readback signal.
        Disregarded if readback attribute is created.
    setpoint_pv : str, optional
        PV prefix of the setpoint signal.
        Disregarded if setpoint attribute is created.
    tolerance : float, optional
        Motion tolerance. The motion is considered *done* when::

            abs(readback-setpoint) <= tolerance

        Defaults to ``10^(-1*precision)``,
        where ``precision = setpoint.precision``.
    use_target : bool
        ``True`` when this object update the ``target`` Component directly.
        Use ``False`` if the ``target`` Component will be updated externally,
        such as by the controller when ``target`` is an ``EpicsSignal``.
        Defaults to ``False``.
    kwargs :
        Passed to `ophyd.PVPositioner`

    ATTRIBUTES

    setpoint : Signal
        The setpoint (request) signal
    readback : Signal or None
        The readback PV (e.g., encoder position PV)
    actuate : Signal or None
        The actuation PV to set when movement is requested
    actuate_value : any, optional
        The actuation value, sent to the actuate signal when motion is
        requested
    stop_signal : Signal or None
        The stop PV to set when motion should be stopped
    stop_value : any, optional
        The value sent to stop_signal when a stop is requested
    target : Signal
        The target value of a move request.

        Override (in subclass) with `EpicsSignal` to connect with a PV.

        In some controllers (such as temperature controllers), the setpoint
        may be changed incrementally towards this target value (such as a
        ramp or controlled trajectory).  In such cases, the ``target`` will
        be final value while ``setpoint`` will be the current desired position.

        Otherwise, both ``setpoint`` and ``target`` will be set to the same value.

    (new in apstools 1.5.3)
    """

    # positioner
    # fmt: off
    readback = FormattedComponent(
        EpicsSignalRO, "{prefix}{_readback_pv}", kind="hinted", auto_monitor=True
    )
    setpoint = FormattedComponent(
        EpicsSignal, "{prefix}{_setpoint_pv}", kind="normal", put_complete=True
    )
    # fmt: on
    done = Component(Signal, value=True, kind="config")
    done_value = True

    tolerance = Component(Signal, value=-1, kind="config")
    report_dmov_changes = Component(Signal, value=False, kind="omitted")

    target = Component(Signal, value=TARGET_UNDEFINED, kind="config")

    def __init__(
        self,
        prefix="",
        *,
        readback_pv="",
        setpoint_pv="",
        tolerance=None,
        use_target=False,
        **kwargs,
    ):
        # fmt: off
        if setpoint_pv == readback_pv:
            raise ValueError(
                f"readback_pv ({readback_pv})"
                f" and setpoint_pv ({setpoint_pv})"
                " must have different values"
            )
        # fmt: on
        self._setpoint_pv = setpoint_pv
        self._readback_pv = readback_pv

        super().__init__(prefix=prefix, **kwargs)

        # Make the default alias for the readback the name of the
        # positioner itself as in EpicsMotor.
        self.readback.name = self.name
        self.use_target = use_target

        self.readback.subscribe(self.cb_readback)
        self.setpoint.subscribe(self.cb_setpoint)
        self.setpoint.subscribe(self.cb_update_target, event_type="setpoint")

        # cancel subscriptions before object is garbage collected
        weakref.finalize(self.readback, self.readback.unsubscribe_all)
        weakref.finalize(self.setpoint, self.setpoint.unsubscribe_all)
        atexit.register(self.cleanup)

        if tolerance:
            self.tolerance.put(tolerance)

    def cleanup(self):
        """Clear subscriptions on exit."""
        self.readback.unsubscribe_all()
        self.setpoint.unsubscribe_all()

    @property
    def actual_tolerance(self):
        tolerance = self.tolerance.get() 
        if tolerance < 0:
            # Use EPICS-defined precision.
            tolerance = 10 ** (-1 * self.precision) 
        return tolerance

    def cb_update_target(self, value, *args, **kwargs):
        self.target.put(value)

    def cb_readback(self, *args, **kwargs):
        """
        Called when readback changes (EPICS CA monitor event) or on-demand.

        Responsible for determining _if_ the positioner is done moving.
        Since soft positioners have no such direct indication, computes
        if the positioner is in position (if a move is active).
        """
        idle = self.done.get() == self.done_value
        if idle:
            return

        if self.inposition:
            self.done.put(self.done_value)
            if self.report_dmov_changes.get():
                logger.debug(f"{self.name} reached: {True}")

    def cb_setpoint(self, *args, **kwargs):
        """
        Called when setpoint changes (EPICS CA monitor event).

        When the setpoint is changed, force`` done=False``.  For any move, ``done``
        **must** transition to ``!= done_value``, then back to ``done_value``.

        Without this response, a small move (within tolerance) will not return.
        The ``cb_readback()`` method will compute ``done``.

        Since other code will also call this method, check the keys in kwargs
        and do not react to the "wrong" signature.
        """
        if "value" in kwargs and "status" not in kwargs:
            self.done.put(not self.done_value)
        logger.debug("cb_setpoint: done=%s, setpoint=%s", self.done.get(), self.setpoint.get())

    @property
    def inposition(self):
        """
        Do readback and setpoint (both from cache) agree within tolerance?

        Returns::

            inposition = |readback - setpoint| <= tolerance
        """
        # Since this method must execute quickly, do NOT force
        # EPICS CA gets using `use_monitor=False`.
        rb = self.readback.get()
        sp = self.setpoint.get() if self.use_target is False else self.target.get()
        tol = self.actual_tolerance
        inpos = math.isclose(rb, sp, abs_tol=tol)
        logger.debug("inposition: inpos=%s rb=%s sp=%s tol=%s", inpos, rb, sp, tol)
        return inpos

    @property
    def precision(self):
        return self.setpoint.precision

    def _setup_move(self, position):
        """Move and do not wait until motion is complete (asynchronous)"""
        self.log.debug("%s.setpoint = %s", self.name, position)
        self.setpoint.put(position, wait=True)
        self.done.put(False)
        if self.actuate is not None:
            self.log.debug("%s.actuate = %s", self.name, self.actuate_value)
            self.actuate.put(self.actuate_value, wait=False)
        self.cb_readback()  # This is needed to force the first check.


class PVPositionerSoftDoneWithStop(PVPositionerSoftDone):
    """
    PVPositionerSoftDone with stop() and inposition.

    The :meth:`stop()` method sets the setpoint to the immediate readback
    value (only when ``inposition`` is ``True``).  This stops the
    positioner at the current position.
    """

    def stop(self, *, success=False):
        """
        Hold the current readback when stop() is called and not :meth:`inposition`.
        """
        import time

        if not self.inposition:
            self.setpoint.put(self.position)
            time.sleep(2.0 / 60)  # two clock ticks, allow for EPICS record processing
            self.cb_readback()  # re-evaluate soft done Signal
