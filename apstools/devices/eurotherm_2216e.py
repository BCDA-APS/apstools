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

from .positioner_soft_done import PVPositionerSoftDoneWithStop

logger = logging.getLogger(__name__)


class Eurotherm2216e(PVPositionerSoftDoneWithStop):
    """
    Eurotherm 2216e Temperature Controller
    """

    readback = Component(EpicsSignalRO, "Temp1", kind="config")
    setpoint = Component(
        EpicsSignal,
        "SetPointTemp",
        kind="hinted",
        write_pv="SetPointTempWrite"
    )
    temp2 = Component(EpicsSignalRO, "Temp2", kind="hinted")
    power = Component(
        EpicsSignal,
        "SetPointPower",
        kind="config",
        write_pv="SetPointPowerWrite"
    )
    sensor = Component(EpicsSignalRO, "SetPointSensor", kind="hinted")

    mode = Component(
        EpicsSignal,
        "SetPointSensor",
        kind="config",
        write_pv="ModeWrite"
    )
    program_number = Component(EpicsSignalRO, "ProgramNumber", kind="config")
    program_status = Component(EpicsSignalRO, "ProgramStatus", kind="config")
