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
import weakref
from typing import Any, Dict, Optional, Union

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd import Signal

logger = logging.getLogger(__name__)


class PTC10AioChannel(Device):
    """
    SRS PTC10 AIO module.

    This class represents an Analog Input/Output module for the PTC10 temperature controller.
    It provides control and monitoring of voltage, limits, I/O type, setpoint, and PID parameters.

    Attributes:
        voltage: Read-only signal for voltage value
        highlimit: Signal with readback for high limit
        lowlimit: Signal with readback for low limit
        iotype: Signal with readback for I/O type
        setpoint: Signal with readback for setpoint
        ramprate: Signal with readback for ramp rate
        ramptemp: Read-only signal for ramp temperature
        offswitch: Signal for off switch
        pidmode: Signal with readback for PID mode
        P: Signal with readback for proportional gain
        I: Signal with readback for integral gain
        D: Signal with readback for derivative gain
        inputchoice: Signal with readback for input choice
        tunelag: Signal with readback for tune lag
        tunestep: Signal with readback for tune step
        tunemode: Signal with readback for tune mode
        tunetype: Signal with readback for tune type
    """

    voltage: EpicsSignalRO = Component(EpicsSignalRO, "voltage_RBV", kind="config")
    highlimit: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "highLimit", kind="config")
    lowlimit: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "lowLimit", kind="config")
    iotype: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "ioType", kind="config", string=True)
    setpoint: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "setPoint", kind="config")
    ramprate: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "rampRate", kind="config")
    ramptemp: EpicsSignalRO = Component(EpicsSignalRO, "rampTemp_RBV", kind="normal")
    offswitch: EpicsSignal = Component(EpicsSignal, "off", kind="config")

    pidmode: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "pid:mode", kind="config", string=True)
    P: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "pid:P", kind="config")
    I: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "pid:I", kind="config")
    D: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "pid:D", kind="config")

    inputchoice: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "pid:input", kind="config", string=True)
    tunelag: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "tune:lag", kind="config")
    tunestep: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "tune:step", kind="config")
    tunemode: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "tune:mode", kind="config", string=True)
    tunetype: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "tune:type", kind="config", string=True)


class PTC10RtdChannel(Device):
    """
    SRS PTC10 RTD module channel.

    This class represents a Resistance Temperature Detector (RTD) module channel
    for the PTC10 temperature controller. It provides monitoring of temperature
    and control of sensor parameters.

    Attributes:
        temperature: Read-only signal for temperature value
        units: Read-only signal for temperature units
        sensor: Signal with readback for sensor type
        channelrange: Signal with readback for channel range
        current: Signal with readback for current setting
        power: Signal with readback for power setting
    """

    temperature: EpicsSignalRO = Component(EpicsSignalRO, "temperature", kind="normal")
    units: EpicsSignalRO = Component(EpicsSignalRO, "units_RBV", kind="config", string=True)
    sensor: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "sensor", kind="config", string=True)
    channelrange: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "range", kind="config", string=True)
    current: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "current", kind="config", string=True)
    power: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "power", kind="config", string=True)


class PTC10TcChannel(Device):
    """
    SRS PTC10 Tc (thermocouple) module channel.

    This class represents a thermocouple module channel for the PTC10 temperature
    controller. It provides monitoring of temperature.

    Attributes:
        temperature: Read-only signal for temperature value
    """

    temperature: EpicsSignalRO = Component(EpicsSignalRO, "temperature", kind="normal")


class PTC10PositionerMixin(Device):
    """
    Mixin so SRS PTC10 can be used as a (temperature) positioner.

    This mixin provides functionality to use the PTC10 as a temperature positioner,
    including position monitoring, movement completion detection, and stopping.

    Attributes:
        done: Signal indicating if movement is complete
        done_value: The value indicating completion (True)
        tolerance: Signal for position tolerance
        report_dmov_changes: Signal for reporting movement changes
        output_enable: Signal for enabling output

    .. autosummary::

       ~cb_readback
       ~cb_setpoint
       ~inposition
       ~stop
    """

    done: Signal = Component(Signal, value=True, kind="omitted")
    done_value: bool = True

    # for computation of soft `done` signal
    # default +/- 1 degree for "at temperature"
    tolerance: Signal = Component(Signal, value=1, kind="config")

    # For logging when temperature is reached after a move.
    report_dmov_changes: Signal = Component(Signal, value=True, kind="omitted")

    output_enable: EpicsSignal = Component(EpicsSignal, "outputEnable", kind="omitted")

    def cb_readback(self, *args: Any, **kwargs: Any) -> None:
        """
        Called when readback changes (EPICS CA monitor event).

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        diff = self.readback.get() - self.setpoint.get()
        dmov = abs(diff) <= self.tolerance.get()
        if self.report_dmov_changes.get() and dmov != self.done.get():
            logger.debug(f"{self.name} reached: {dmov}")
        self.done.put(dmov)

    def cb_setpoint(self, *args: Any, **kwargs: Any) -> None:
        """
        Called when setpoint changes (EPICS CA monitor event).

        When the setpoint is changed, force ``done=False``.  For any move,
        ``done`` MUST change to ``!= done_value``, then change back to
        ``done_value (True)``.  Without this response, a small move
        (within tolerance) will not return.  Next update of readback
        will compute ``self.done``.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        self.done.put(not self.done_value)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the PTC10 positioner mixin.

        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.readback.name = self.name

        # to compute the soft `done` signal
        self.readback.subscribe(self.cb_readback)
        self.setpoint.subscribe(self.cb_setpoint)
        # cancel subscriptions before object is garbage collected
        weakref.finalize(self.readback, self.readback.unsubscribe_all)
        weakref.finalize(self.setpoint, self.setpoint.unsubscribe_all)

    @property
    def inposition(self) -> bool:
        """
        Check if the device is in position.

        Returns:
            bool: True if the device is in position
        """
        return self.done.get()

    def stop(self, *, success: bool = False) -> None:
        """
        Stop the device.

        Args:
            success: Whether the stop was successful
        """
        self.output_enable.put(0)
        self.done.put(True)


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
