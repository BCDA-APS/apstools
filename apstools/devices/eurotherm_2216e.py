"""
Eurotherm 2216e Temperature Controller
++++++++++++++++++++++++++++++++++++++

The 2216e is a temperature controller from Eurotherm.

.. autosummary::

   ~Eurotherm2216e

According to their website, the [Eurotherm 2216e Temperature
Controller](https://www.eurothermcontrollers.com/eurotherm-2216e-series-controller-now-obsolete/)
is obsolete.  Please see replacement
[EPC3016](https://www.eurothermcontrollers.com/eurotherm-epc3016-1-16-din-process-and-temperature-controller/)
in our [EPC3000 Series](https://www.eurothermcontrollers.com/epc3000-series).

New in apstools 1.6.0.
"""

import logging

from ophyd import Component
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import Signal

from .positioner_soft_done import PVPositionerSoftDoneWithStop

logger = logging.getLogger(__name__)


class Eurotherm2216e(PVPositionerSoftDoneWithStop):
    """
    Eurotherm 2216e Temperature Controller
    """

    # temperature value in dC, needs conversion: readback = 0.1 * sensor
    sensor = Component(EpicsSignalRO, "SetPointSensor", kind="omitted")
    readback = Component(Signal, value=0, kind="hinted")
    setpoint = Component(
        EpicsSignal,
        "SetPointTemp",
        kind="hinted",
        write_pv="SetPointTempWrite",
        put_complete=True,
    )
    # temp1 & temp2 PVs have no useful values : ignore here
    # temp1 = Component(EpicsSignalRO, "Temp1", kind="hinted")
    # temp2 = Component(EpicsSignalRO, "Temp2", kind="hinted")
    power = Component(
        EpicsSignal,
        "SetPointPower",
        kind="config",
        write_pv="SetPointPowerWrite",
        put_complete=True,
    )

    mode = Component(
        EpicsSignal,
        "SetPointSensor",
        kind="config",
        write_pv="ModeWrite",
        string=True,
    )
    program_number = Component(EpicsSignalRO, "ProgramNumber", kind="config")
    # program_status = Component(
    #     EpicsSignalRO,
    #     "ProgramStatus",
    #     kind="config",
    #     string=True
    # )

    target = None  # remove from PVPositionerSoftDoneWithStop

    def cb_sensor(self, *args, **kwargs):
        "units: Convert dC from sensor to C"
        self.readback.put(0.1 * self.sensor.get())

    def __init__(
        self, prefix="", *, tolerance=None, update_target=True, **kwargs
    ):
        super().__init__(
            prefix=prefix,
            readback_pv="ignoreRBV",
            setpoint_pv="ignore",
            tolerance=tolerance,
            update_target=update_target,
            **kwargs
        )
        self.update_target = False  # remove from PVPositionerSoftDoneWithStop
        self.sensor.subscribe(self.cb_sensor)
        self.tolerance.put(1)  # because setpoint is integer
