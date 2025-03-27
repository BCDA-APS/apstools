"""
Linkam temperature controllers
++++++++++++++++++++++++++++++

.. autosummary::

   ~Linkam_CI94_Device
   ~Linkam_T96_Device
"""

from typing import Any

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd import Signal

from . import PVPositionerSoftDoneWithStop


class Linkam_CI94_Device(Device):
    """
    Linkam model CI94 temperature controller

    EXAMPLE::

        ci94 = Linkam_CI94_Device("IOC:ci94:", name="ci94")
    """

    controller_name: str = "Linkam CI94"

    temperature: PVPositionerSoftDoneWithStop = Component(
        PVPositionerSoftDoneWithStop,
        "",
        readback_pv="temp",
        setpoint_pv="setLimit",
        tolerance=1.0,
        kind="hinted",
    )

    units: Signal = Component(Signal, value="C", kind="config")

    temperature_in: EpicsSignalRO = Component(EpicsSignalRO, "tempIn", kind="omitted")
    # DO NOT USE: temperature2_in = Component(EpicsSignalRO, "temp2In", kind="omitted")
    # DO NOT USE: temperature2 = Component(EpicsSignalRO, "temp2")

    dsc_in: EpicsSignalRO = Component(EpicsSignalRO, "dscIn", kind="omitted")
    end_after_profile: EpicsSignal = Component(EpicsSignal, "endAfterProfile", kind="omitted")
    end_on_stop: EpicsSignal = Component(EpicsSignal, "endOnStop", kind="omitted")
    error_byte: EpicsSignalRO = Component(EpicsSignalRO, "errorByte", kind="omitted")
    gen_stat: EpicsSignalRO = Component(EpicsSignalRO, "genStat", kind="omitted")
    hold_control: EpicsSignal = Component(EpicsSignal, "hold", kind="omitted")
    pump_mode: EpicsSignal = Component(EpicsSignal, "pumpMode", kind="omitted")
    pump_speed: EpicsSignalRO = Component(EpicsSignalRO, "pumpSpeed", kind="omitted")
    pump_speed_in: EpicsSignalRO = Component(EpicsSignalRO, "pumpSpeedIn", kind="omitted")
    rate: EpicsSignal = Component(EpicsSignal, "setRate", kind="omitted")  # RPM

    speed: EpicsSignal = Component(EpicsSignal, "setSpeed", kind="config")
    # deg/min, speed 0 = automatic control

    start_control: EpicsSignal = Component(EpicsSignal, "start", kind="omitted")
    status: EpicsSignalRO = Component(EpicsSignalRO, "status", kind="omitted")
    status_in: EpicsSignalRO = Component(EpicsSignalRO, "statusIn", kind="omitted")
    stop_control: EpicsSignal = Component(EpicsSignal, "stop", kind="omitted")

    # clear_buffer = Component(EpicsSignal, "clearBuffer", kind="omitted")  # bo
    # scan_dis = Component(EpicsSignal, "scanDis", kind="omitted")          # bo
    # test = Component(EpicsSignal, "test", kind="omitted")                 # longout
    # d_cmd = Component(EpicsSignalRO, "DCmd", kind="omitted")              # ai
    # t_cmd = Component(EpicsSignalRO, "TCmd", kind="omitted")              # ai
    # dsc = Component(EpicsSignalRO, "dsc", kind="omitted")                 # calc

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize Linkam_CI94_Device."""
        super().__init__(*args, **kwargs)

        # temperature component is the main value
        self.temperature.name = self.name


class T96Temperature(PVPositionerSoftDoneWithStop):
    """Temperature controller for T96."""

    actuate: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "heating", kind="config", string=True)
    actuate_value: str = "On"


class Linkam_T96_Device(Device):
    """
    Linkam model T96 temperature controller

    EXAMPLE::

        tc1 = Linkam_T96("IOC:tc1:", name="tc1")
    """

    controller_name: str = "Linkam T96"

    temperature: T96Temperature = Component(
        T96Temperature,
        "",
        readback_pv="temperature_RBV",
        setpoint_pv="rampLimit",
        tolerance=1.0,
        kind="hinted",
    )

    ramprate: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "rampRate", kind="config")
    units: Signal = Component(Signal, value="C", kind="config")

    controller_config: EpicsSignalRO = Component(EpicsSignalRO, "controllerConfig_RBV", kind="omitted")
    controller_error: EpicsSignalRO = Component(EpicsSignalRO, "controllerError_RBV", kind="omitted")
    controller_status: EpicsSignalRO = Component(EpicsSignalRO, "controllerStatus_RBV", kind="omitted")
    heater_power: EpicsSignalRO = Component(EpicsSignalRO, "heaterPower_RBV", kind="omitted")
    lnp_mode: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "lnpMode", kind="omitted")
    lnp_speed: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "lnpSpeed", kind="omitted")
    lnp_status: EpicsSignalRO = Component(EpicsSignalRO, "lnpStatus_RBV", kind="omitted")
    pressure: EpicsSignalRO = Component(EpicsSignalRO, "pressure_RBV", kind="omitted")
    ramp_at_limit: EpicsSignalRO = Component(EpicsSignalRO, "rampAtLimit_RBV", kind="omitted")
    stage_config: EpicsSignalRO = Component(EpicsSignalRO, "stageConfig_RBV", kind="omitted")
    status_error: EpicsSignalRO = Component(EpicsSignalRO, "statusError_RBV", kind="omitted")
    vacuum: EpicsSignal = Component(EpicsSignal, "vacuum", kind="omitted")
    vacuum_at_limit: EpicsSignalRO = Component(EpicsSignalRO, "vacuumAtLimit_RBV", kind="omitted")
    vacuum_limit_readback: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "vacuumLimit", kind="omitted")
    vacuum_status: EpicsSignalRO = Component(EpicsSignalRO, "vacuumStatus_RBV", kind="omitted")  # calc

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize Linkam_T96_Device."""
        super().__init__(*args, **kwargs)

        # temperature component is the main value
        self.temperature.name = self.name


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
