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
from ophyd.signal import EpicsSignalBase

from ..tests import timed_pause

logger = logging.getLogger(__name__)

# Must use a data type that can be serialized as json (Python's None cannot be serialized)
# This ValueError: Cannot determine the appropriate bluesky-friendly data type for value
# None of Python type <class 'NoneType'>. Supported types include: int, float, str, and
# iterables such as list, tuple, np.ndarray, and so on.
TARGET_UNDEFINED = "undefined"


class _EpicsPositionerSetpointSignal(EpicsSignal):
    """
    Special handling when PVPositionerSoftDone setpoint is changed.

    When the setpoint is changed, force`` done=False``.  For any move, ``done``
    **must** transition to ``!= done_value``, then back to ``done_value``.
    Without this response, a small move (within tolerance) will not return.
    The ``cb_readback()`` method will compute ``done``.
    """

    def put(self, value, *args, **kwargs):
        """Make sure 'done' signal goes False when setpoint is changed by us."""
        super().put(value, *args, **kwargs)

        self.parent.done.put(not self.parent.done_value)
        if self.parent.update_target:
            kwargs = {}
            if issubclass(self.parent.target.__class__, EpicsSignalBase):
                kwargs["wait"] = True  # Signal.put() warns if kwargs are given
            self.parent.target.put(value, **kwargs)

    # def get(self, *args, **kwargs):
    #     value = super().get(*args, **kwargs)
    #     if self.parent.update_target:
    #         target = self.parent.target.get()
    #         if target != TARGET_UNDEFINED:
    #             value = target
    #     return value


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
    update_target : bool
        ``True`` when this object updates the ``target`` Component directly.
        Use ``False`` if the ``target`` Component will be updated externally,
        such as by the controller when ``target`` is an ``EpicsSignal``.
        Defaults to ``True``.
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
        _EpicsPositionerSetpointSignal, "{prefix}{_setpoint_pv}", kind="normal", put_complete=True
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
        update_target=True,
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
        self.update_target = update_target

        self.readback.subscribe(self.cb_readback)
        self.setpoint.subscribe(self.cb_setpoint)
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

    # fmt: off
    @property
    def actual_tolerance(self):
        return (
            self.tolerance.get()
            if self.tolerance.get() >= 0
            else 10 ** (-1 * self.precision)
        )
    # fmt: on

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

        This method is called when the setpoint is changed by this code or from
        some other EPICS client.

        The 'done' signal is set to False in the custom
        _EpicsPositionerSetpointSignal class.
        """
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
        sp = self.setpoint.get()
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

        # Write the setpoint value.
        self.setpoint.put(position, wait=True)
        # The 'done' and 'target' signals are handled by
        # the custom '_EpicsPositionerSetpointSignal' class.

        if self.actuate is not None:
            self.log.debug("%s.actuate = %s", self.name, self.actuate_value)
            self.actuate.put(self.actuate_value, wait=False)

        # Force the first check for done.
        self.cb_readback()


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
        if not self.inposition:
            self.setpoint.put(self.position)
            timed_pause()
            self.cb_readback()  # re-evaluate soft done Signal


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
