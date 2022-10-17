"""
PVPositioner that computes ``done`` as a soft signal.

.. autosummary::

   ~PVPositionerSoftDone
   ~PVPositionerSoftDoneWithStop
"""

from ..tests import short_delay_for_EPICS_IOC_database_processing
from ophyd import Component
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent
from ophyd import PVPositioner
from ophyd import Signal
from ophyd.signal import EpicsSignalBase
import logging


logger = logging.getLogger(__name__)


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
        ``True`` when this object update the ``target`` Component directly.
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
    readback = FormattedComponent(
        EpicsSignalRO, "{prefix}{_readback_pv}", kind="hinted", auto_monitor=True
    )
    setpoint = FormattedComponent(
        EpicsSignal, "{prefix}{_setpoint_pv}", kind="normal", put_complete=True
    )
    done = Component(Signal, value=True, kind="config")
    done_value = True

    tolerance = Component(Signal, value=-1, kind="config")
    report_dmov_changes = Component(Signal, value=False, kind="omitted")

    target = Component(Signal, value="None", kind="config")

    _rb_count = 0
    _sp_count = 0

    @property
    def precision(self):
        return self.setpoint.precision

    @property
    def actual_tolerance(self):
        return (
            self.tolerance.get()
            if self.tolerance.get() >= 0
            else 10 ** (-1 * self.precision)
        )

    def cb_readback(self, *args, **kwargs):
        """
        Called when readback changes (EPICS CA monitor event).

        Computes if the positioner is done moving::

            done = |readback - setpoint| <= tolerance
        """
        self._rb_count += 1
        if "value" in kwargs:
            diff = kwargs["value"] - self.setpoint.get()
        else:
            diff = self.readback.get(use_monitor=False) - self.setpoint.get()
        dmov = abs(diff) <= self.actual_tolerance
        if self.report_dmov_changes.get() and dmov != self.done.get():
            logger.debug("%s reached: %s", self.name, dmov)

        v = self.done_value
        self.done.put({True: v, False: not v}[dmov])
        logger.debug("cb_readback: done=%s, position=%s", self.done.get(), self.position)

    def cb_setpoint(self, *args, **kwargs):
        """
        Called when setpoint changes (EPICS CA monitor event).

        When the setpoint is changed, force done=False.  For any move, done
        **must** transition to ``!= done_value``, then back to ``done_value``.

        Without this response, a small move (within tolerance) will not return.
        Next update of readback will compute ``self.done``.
        """
        self._sp_count += 1
        self.done.put(not self.done_value)
        logger.debug("cb_setpoint: done=%s, setpoint=%s", self.done.get(), self.setpoint.get())

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

        if setpoint_pv == readback_pv:
            raise ValueError(
                f"readback_pv ({readback_pv})"
                f" and setpoint_pv ({setpoint_pv})"
                " must have different values"
            )
        self._setpoint_pv = setpoint_pv
        self._readback_pv = readback_pv

        super().__init__(prefix=prefix, **kwargs)

        # Make the default alias for the readback the name of the
        # positioner itself as in EpicsMotor.
        self.readback.name = self.name
        self.update_target = update_target

        self.readback.subscribe(self.cb_readback)
        self.setpoint.subscribe(self.cb_setpoint)
        if tolerance:
            self.tolerance.put(tolerance)

    def _setup_move(self, position):
        """Move and do not wait until motion is complete (asynchronous)"""
        self.log.debug("%s.setpoint = %s", self.name, position)
        if self.update_target:
            kwargs = {}
            if issubclass(self.target.__class__, EpicsSignalBase):
                kwargs["wait"] = True  # Signal.put() warns if kwargs are given
            self.target.put(position, **kwargs)
        self.setpoint.put(position, wait=True)
        if self.actuate is not None:
            self.log.debug("%s.actuate = %s", self.name, self.actuate_value)
            self.actuate.put(self.actuate_value, wait=False)
        # This is needed because in a special case the setpoint.put does not
        # run the "sub_value" subscriptions.
        self.cb_setpoint()
        self.cb_readback()  # This is needed to force the first check.


class PVPositionerSoftDoneWithStop(PVPositionerSoftDone):
    """
    PVPositionerSoftDone with stop() and inposition.

    The :meth:`stop()` method sets the setpoint to the immediate readback
    value (only when ``inposition`` is ``True``).  This stops the
    positioner at the current position.
    """

    @property
    def inposition(self):
        """
        Report (boolean) if positioner is done.
        """
        return self.done.get() == self.done_value

    def stop(self, *, success=False):
        """
        Hold the current readback when stop() is called and not :meth:`inposition`.
        """
        if not self.inposition:
            self.setpoint.put(self.position)
            short_delay_for_EPICS_IOC_database_processing()
            self.cb_readback()  # re-evaluate soft done Signal

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
