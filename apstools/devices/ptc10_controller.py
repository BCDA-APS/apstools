"""
PTC10 Programmable Temperature Controller
+++++++++++++++++++++++++++++++++++++++++

The PTC10 is a programmable temperature controller from SRS (Stanford Research
Systems).  The PTC10 is a modular system consisting of a base unit and provision
for addition of add-on boards.

A single, complete ``ophyd.Device`` subclass will not describe all variations
that could be installed. But the add-on boards each allow standardization. Each
installation must build a custom class that matches their hardware
configuration.  The APS USAXS instrument has created a `custom class
<https://github.com/APS-USAXS/ipython-usaxs/blob/master/profile_bluesky/startup/instrument/devices/ptc10_controller.py#L59-L159>`_
based on the `ophyd.PVPositioner` to use their `PTC10` as a temperature
*positioner*.

.. autosummary::

   ~PTC10AioChannel
   ~PTC10RtdChannel
   ~PTC10TcChannel
   ~PTC10PositionerMixin

:see: https://www.thinksrs.com/products/ptc10.html

EXAMPLE::

    from ophyd import PVPositioner

    class MyPTC10(PTC10PositionerMixin, PVPositioner):
        readback = Component(EpicsSignalRO, "2A:temperature", kind="hinted")
        setpoint = Component(EpicsSignalWithRBV, "5A:setPoint", kind="hinted")

        rtd = Component(PTC10RtdChannel, "3A:")
        pid = Component(PTC10AioChannel, "5A:")

    ptc10 = MyPTC10("IOC_PREFIX:ptc10:", name="ptc10")
    ptc10.report_dmov_changes.put(True)  # a diagnostic
    ptc10.tolerance.put(1.0)  # done when |readback-setpoint|<=tolerance

New in apstools 1.5.3.
"""

import logging

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd import Signal

logger = logging.getLogger(__name__)


class PTC10AioChannel(Device):
    """
    SRS PTC10 AIO module
    """

    voltage = Component(EpicsSignalRO, "voltage_RBV", kind="config")
    highlimit = Component(EpicsSignalWithRBV, "highLimit", kind="config")
    lowlimit = Component(EpicsSignalWithRBV, "lowLimit", kind="config")
    iotype = Component(EpicsSignalWithRBV, "ioType", kind="config", string=True)
    setpoint = Component(EpicsSignalWithRBV, "setPoint", kind="config")
    ramprate = Component(EpicsSignalWithRBV, "rampRate", kind="config")
    offswitch = Component(EpicsSignal, "off", kind="config")

    pidmode = Component(EpicsSignalWithRBV, "pid:mode", kind="config", string=True)
    P = Component(EpicsSignalWithRBV, "pid:P", kind="config")
    I = Component(EpicsSignalWithRBV, "pid:I", kind="config")
    D = Component(EpicsSignalWithRBV, "pid:D", kind="config")

    inputchoice = Component(EpicsSignalWithRBV, "pid:input", kind="config", string=True)
    tunelag = Component(EpicsSignalWithRBV, "tune:lag", kind="config")
    tunestep = Component(EpicsSignalWithRBV, "tune:step", kind="config")
    tunemode = Component(EpicsSignalWithRBV, "tune:mode", kind="config", string=True)
    tunetype = Component(EpicsSignalWithRBV, "tune:type", kind="config", string=True)


class PTC10RtdChannel(Device):
    """
    SRS PTC10 RTD module channel
    """

    temperature = Component(EpicsSignalRO, "temperature", kind="normal")
    units = Component(EpicsSignalRO, "units_RBV", kind="config", string=True)
    sensor = Component(EpicsSignalWithRBV, "sensor", kind="config", string=True)
    channelrange = Component(EpicsSignalWithRBV, "range", kind="config", string=True)
    current = Component(EpicsSignalWithRBV, "current", kind="config", string=True)
    power = Component(EpicsSignalWithRBV, "power", kind="config", string=True)


class PTC10TcChannel(Device):
    """
    SRS PTC10 Tc (thermocouple) module channel
    """

    temperature = Component(EpicsSignalRO, "temperature", kind="normal")


class PTC10PositionerMixin(Device):
    """
    Mixin so SRS PTC10 can be used as a (temperature) positioner.

    .. autosummary::

       ~cb_readback
       ~cb_setpoint
       ~inposition
       ~stop
    """

    done = Component(Signal, value=True, kind="omitted")
    done_value = True

    # for computation of soft `done` signal
    # default +/- 1 degree for "at temperature"
    tolerance = Component(Signal, value=1, kind="config")

    # For logging when temperature is reached after a move.
    report_dmov_changes = Component(Signal, value=True, kind="omitted")

    def cb_readback(self, *args, **kwargs):
        """
        Called when readback changes (EPICS CA monitor event).
        """
        diff = self.readback.get() - self.setpoint.get()
        dmov = abs(diff) <= self.tolerance.get()
        if self.report_dmov_changes.get() and dmov != self.done.get():
            logger.debug(f"{self.name} reached: {dmov}")
        self.done.put(dmov)

    def cb_setpoint(self, *args, **kwargs):
        """
        Called when setpoint changes (EPICS CA monitor event).

        When the setpoint is changed, force ``done=False``.  For any move,
        ``done`` MUST change to ``!= done_value``, then change back to
        ``done_value (True)``.  Without this response, a small move
        (within tolerance) will not return.  Next update of readback
        will compute ``self.done``.
        """
        self.done.put(not self.done_value)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.readback.name = self.name

        # to compute the soft `done` signal
        self.readback.subscribe(self.cb_readback)
        self.setpoint.subscribe(self.cb_setpoint)

    @property
    def inposition(self):
        """
        Report (boolean) if positioner is done.
        """
        return self.done.get() == self.done_value

    def stop(self, *, success=False):
        """
        Hold the current readback when the stop() method is called and not done.
        """
        if not self.done.get():
            self.setpoint.put(self.position)

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
