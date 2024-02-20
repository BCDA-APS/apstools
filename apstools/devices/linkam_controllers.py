"""
Linkam temperature controllers
++++++++++++++++++++++++++++++

.. autosummary::

   ~Linkam_CI94_Device
   ~Linkam_T96_Device
"""

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

    controller_name = "Linkam CI94"

    temperature = Component(
        PVPositionerSoftDoneWithStop,
        "",
        readback_pv="temp",
        setpoint_pv="setLimit",
        tolerance=1.0,
        kind="hinted",
    )

    units = Component(Signal, value="C", kind="config")

    temperature_in = Component(EpicsSignalRO, "tempIn", kind="omitted")
    # DO NOT USE: temperature2_in = Component(EpicsSignalRO, "temp2In", kind="omitted")
    # DO NOT USE: temperature2 = Component(EpicsSignalRO, "temp2")

    dsc_in = Component(EpicsSignalRO, "dscIn", kind="omitted")
    end_after_profile = Component(EpicsSignal, "endAfterProfile", kind="omitted")
    end_on_stop = Component(EpicsSignal, "endOnStop", kind="omitted")
    error_byte = Component(EpicsSignalRO, "errorByte", kind="omitted")
    gen_stat = Component(EpicsSignalRO, "genStat", kind="omitted")
    hold_control = Component(EpicsSignal, "hold", kind="omitted")
    pump_mode = Component(EpicsSignal, "pumpMode", kind="omitted")
    pump_speed = Component(EpicsSignalRO, "pumpSpeed", kind="omitted")
    pump_speed_in = Component(EpicsSignalRO, "pumpSpeedIn", kind="omitted")
    rate = Component(EpicsSignal, "setRate", kind="omitted")  # RPM

    speed = Component(EpicsSignal, "setSpeed", kind="config")
    # deg/min, speed 0 = automatic control

    start_control = Component(EpicsSignal, "start", kind="omitted")
    status = Component(EpicsSignalRO, "status", kind="omitted")
    status_in = Component(EpicsSignalRO, "statusIn", kind="omitted")
    stop_control = Component(EpicsSignal, "stop", kind="omitted")

    # clear_buffer = Component(EpicsSignal, "clearBuffer", kind="omitted")  # bo
    # scan_dis = Component(EpicsSignal, "scanDis", kind="omitted")          # bo
    # test = Component(EpicsSignal, "test", kind="omitted")                 # longout
    # d_cmd = Component(EpicsSignalRO, "DCmd", kind="omitted")              # ai
    # t_cmd = Component(EpicsSignalRO, "TCmd", kind="omitted")              # ai
    # dsc = Component(EpicsSignalRO, "dsc", kind="omitted")                 # calc

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # temperature component is the main value
        self.temperature.name = self.name


class T96Temperature(PVPositionerSoftDoneWithStop):
    actuate = Component(EpicsSignalWithRBV, "heating", kind="config", string=True)
    actuate_value = "On"


class Linkam_T96_Device(Device):
    """
    Linkam model T96 temperature controller

    EXAMPLE::

        tc1 = Linkam_T96("IOC:tc1:", name="tc1")
    """

    controller_name = "Linkam T96"

    temperature = Component(
        T96Temperature,
        "",
        readback_pv="temperature_RBV",
        setpoint_pv="rampLimit",
        tolerance=1.0,
        kind="hinted",
    )

    ramprate = Component(EpicsSignalWithRBV, "rampRate", kind="config")
    units = Component(Signal, value="C", kind="config")

    controller_config = Component(EpicsSignalRO, "controllerConfig_RBV", kind="omitted")
    controller_error = Component(EpicsSignalRO, "controllerError_RBV", kind="omitted")
    controller_status = Component(EpicsSignalRO, "controllerStatus_RBV", kind="omitted")
    heater_power = Component(EpicsSignalRO, "heaterPower_RBV", kind="omitted")
    lnp_mode = Component(EpicsSignalWithRBV, "lnpMode", kind="omitted")
    lnp_speed = Component(EpicsSignalWithRBV, "lnpSpeed", kind="omitted")
    lnp_status = Component(EpicsSignalRO, "lnpStatus_RBV", kind="omitted")
    pressure = Component(EpicsSignalRO, "pressure_RBV", kind="omitted")
    ramp_at_limit = Component(EpicsSignalRO, "rampAtLimit_RBV", kind="omitted")
    stage_config = Component(EpicsSignalRO, "stageConfig_RBV", kind="omitted")
    status_error = Component(EpicsSignalRO, "statusError_RBV", kind="omitted")
    vacuum = Component(EpicsSignal, "vacuum", kind="omitted")
    vacuum_at_limit = Component(EpicsSignalRO, "vacuumAtLimit_RBV", kind="omitted")
    vacuum_limit_readback = Component(EpicsSignalWithRBV, "vacuumLimit", kind="omitted")
    vacuum_status = Component(EpicsSignalRO, "vacuumStatus_RBV", kind="omitted")  # calc

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # temperature component is the main value
        self.temperature.name = self.name


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
