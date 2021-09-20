"""
PVPositioner that computes ``done`` as a soft signal.
"""

from ophyd import Component
from ophyd import FormattedComponent
from ophyd import PVPositioner
from ophyd import Signal
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
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

        In some controllers (such as temperature controllers),
        the setpoint may be changed incrementally
        towards this target value (such as a ramp or controlled trajectory).
        In such cases, the ``target`` will be final value while ``setpoint``
        will be the current desired position.

        Otherwise, both ``setpoint`` and ``target`` will be set to the same value.

    (new in apstools 1.5.2)
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

    target = Component(Signal, value=None, kind="config")

    @property
    def precision(self):
        return self.setpoint.precision

    def cb_readback(self, *args, **kwargs):
        """
        Called when readback changes (EPICS CA monitor event).
        """
        diff = self.readback.get() - self.setpoint.get()
        _tolerance = (
            self.tolerance.get()
            if self.tolerance.get() >= 0
            else 10 ** (-1 * self.precision)
        )
        dmov = abs(diff) <= _tolerance
        if self.report_dmov_changes.get() and dmov != self.done.get():
            logger.debug(f"{self.name} reached: {dmov}")
        self.done.put(dmov)

    def cb_setpoint(self, *args, **kwargs):
        """
        Called when setpoint changes (EPICS CA monitor event).
        When the setpoint is changed, force done=False.  For any move,
        done must go != done_value, then back to done_value (True).
        Without this response, a small move (within tolerance) will not return.
        Next update of readback will compute self.done.
        """
        self.done.put(not self.done_value)

    def __init__(
        self,
        prefix="",
        *,
        readback_pv="",
        setpoint_pv="",
        tolerance=None,
        **kwargs,
    ):

        self._setpoint_pv = setpoint_pv
        self._readback_pv = readback_pv

        super().__init__(prefix=prefix, **kwargs)

        # Make the default alias for the readback the name of the
        # positioner itself as in EpicsMotor.
        self.readback.name = self.name

        self.readback.subscribe(self.cb_readback)
        self.setpoint.subscribe(self.cb_setpoint)
        if tolerance:
            self.tolerance.put(tolerance)

    def _setup_move(self, position):
        """Move and do not wait until motion is complete (asynchronous)"""
        self.log.debug("%s.setpoint = %s", self.name, position)
        kwargs = {}
        if issubclass(self.target.__class__, EpicsSignalBase):
            kwargs["wait"] = True  # Signal.put() warns if kwargs are given
        self.target.put(position, **kwargs)
        self.setpoint.put(position, wait=True)
        if self.actuate is not None:
            self.log.debug("%s.actuate = %s", self.name, self.actuate_value)
            self.actuate.put(self.actuate_value, wait=False)
        self.cb_readback()  # This is needed to force the first check.
