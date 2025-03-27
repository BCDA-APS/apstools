"""
Measurement Computing USB-CTR 8-Channel Scaler
++++++++++++++++++++++++++++++++++++++++++++++++++

Measurement Computing CTR High-Speed Counter/Timer Device

https://www.farnell.com/datasheets/3795358.pdf

There is more to this device than just the 8-channel scaler.
Underlying support: https://github.com/epics-modules/measComp


The EPICS support provides for an optional scaler, compatible
with the EPICS scaler record.

*new in apstools release 1.6.18*

.. rubric:: Public class(es)
.. autosummary::

   ~MeasCompCtr
   ~MeasCompCtrMcs

.. rubric:: Internal class(es)
.. autosummary::

   ~MeasCompCtrDeviceCounterChannel
   ~MeasCompCtrDevicePulseGenChannel
"""


import logging
from typing import Any

logger = logging.getLogger(__name__)

logger.info(__file__)

from ophyd import Component, Device, EpicsSignal, EpicsSignalRO, EpicsSignalWithRBV


class MeasCompCtrMcs(Device):
    """Measurement Computing USB CTR08 Multi-Channel Scaler Controls."""

    # https://github.com/epics-modules/measComp/blob/master/measCompApp/Db/measCompMCS.template
    absolute_timebase_waveform: EpicsSignal = Component(EpicsSignal, "AbsTimeWF")
    acquiring: EpicsSignal = Component(EpicsSignal, "Acquiring", kind="config")
    channel_advance: EpicsSignal = Component(EpicsSignal, "ChannelAdvance", kind="config")
    client_wait: EpicsSignal = Component(EpicsSignal, "ClientWait", kind="config")
    current_channel: EpicsSignalRO = Component(EpicsSignalRO, "CurrentChannel", kind="omitted")
    do_read_all: EpicsSignal = Component(EpicsSignal, "DoReadAll", kind="omitted")
    dwell: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Dwell", kind="config")
    elapsed_real: EpicsSignalRO = Component(EpicsSignalRO, "ElapsedReal")
    enable_client_wait: EpicsSignal = Component(EpicsSignal, "EnableClientWait", kind="config")
    erase_all: EpicsSignal = Component(EpicsSignal, "EraseAll", kind="omitted")
    erase_start: EpicsSignal = Component(EpicsSignal, "EraseStart", kind="omitted")
    hardware_acquiring: EpicsSignalRO = Component(EpicsSignalRO, "HardwareAcquiring", kind="config")
    max_channels: EpicsSignalRO = Component(EpicsSignalRO, "MaxChannels", kind="config")
    mcs_counter_1_enable: EpicsSignal = Component(EpicsSignal, "MCSCounter1Enable", kind="config")
    mcs_counter_2_enable: EpicsSignal = Component(EpicsSignal, "MCSCounter2Enable", kind="config")
    mcs_counter_3_enable: EpicsSignal = Component(EpicsSignal, "MCSCounter3Enable", kind="config")
    mcs_counter_4_enable: EpicsSignal = Component(EpicsSignal, "MCSCounter4Enable", kind="config")
    mcs_counter_5_enable: EpicsSignal = Component(EpicsSignal, "MCSCounter5Enable", kind="config")
    mcs_counter_6_enable: EpicsSignal = Component(EpicsSignal, "MCSCounter6Enable", kind="config")
    mcs_counter_7_enable: EpicsSignal = Component(EpicsSignal, "MCSCounter7Enable", kind="config")
    mcs_counter_8_enable: EpicsSignal = Component(EpicsSignal, "MCSCounter8Enable", kind="config")
    mcs_counter_enable: EpicsSignal = Component(EpicsSignal, "MCSCounterEnable", kind="config")
    mcs_dio_enable: EpicsSignal = Component(EpicsSignal, "MCSDIOEnable", kind="config")
    model: EpicsSignalRO = Component(EpicsSignalRO, "Model", kind="config", string=True)
    n_use_all: EpicsSignal = Component(EpicsSignal, "NuseAll", kind="omitted")
    point_0_action: EpicsSignal = Component(EpicsSignal, "Point0Action", kind="config")
    prescale: EpicsSignal = Component(EpicsSignal, "Prescale", kind="config")
    prescale_counter: EpicsSignal = Component(EpicsSignal, "PrescaleCounter", kind="config")
    preset_real: EpicsSignal = Component(EpicsSignal, "PresetReal", kind="config")
    read_all: EpicsSignal = Component(EpicsSignal, "ReadAll", kind="omitted")
    read_all_once: EpicsSignal = Component(EpicsSignal, "ReadAllOnce", kind="omitted")
    set_acquiring: EpicsSignal = Component(EpicsSignal, "SetAcquiring", kind="omitted")
    set_client_wait: EpicsSignal = Component(EpicsSignal, "SetClientWait", kind="config")
    snl_connected: EpicsSignalRO = Component(EpicsSignalRO, "SNL_Connected", kind="config")
    start_all: EpicsSignal = Component(EpicsSignal, "StartAll", kind="omitted")
    stop_all: EpicsSignal = Component(EpicsSignal, "StopAll", kind="omitted")
    trigger_mode: EpicsSignal = Component(EpicsSignal, "TrigMode", kind="config", string=True)

    mca1: EpicsSignalRO = Component(EpicsSignalRO, "mca1", labels=["MCA"])
    mca2: EpicsSignalRO = Component(EpicsSignalRO, "mca2", labels=["MCA"])
    mca3: EpicsSignalRO = Component(EpicsSignalRO, "mca3", labels=["MCA"])
    mca4: EpicsSignalRO = Component(EpicsSignalRO, "mca4", labels=["MCA"])
    mca5: EpicsSignalRO = Component(EpicsSignalRO, "mca5", labels=["MCA"])
    mca6: EpicsSignalRO = Component(EpicsSignalRO, "mca6", labels=["MCA"])
    mca7: EpicsSignalRO = Component(EpicsSignalRO, "mca7", labels=["MCA"])
    mca8: EpicsSignalRO = Component(EpicsSignalRO, "mca8", labels=["MCA"])


class MeasCompCtrDeviceCounterChannel(Device):
    """Measurement Computing USB CTR08 Pulse Counter channel."""

    counts: EpicsSignalRO = Component(EpicsSignalRO, "Counts")
    reset: EpicsSignal = Component(EpicsSignal, "Reset", kind="omitted")


class MeasCompCtrDevicePulseGenChannel(Device):
    """Measurement Computing USB CTR08 Pulse Generator channel."""

    # Do not connect: (calcout) CalcDutyCycle
    # Do not connect: (calcout) CalcFrequency
    # Do not connect: (calcout) CalcPeriod
    # Do not connect: (calcout) CalcWidth
    count: EpicsSignal = Component(EpicsSignal, "Count")
    delay: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Delay")
    duty_cycle: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "DutyCycle")
    frequency: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Frequency")
    idle_state: EpicsSignal = Component(EpicsSignal, "IdleState")
    period: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Period")
    run: EpicsSignal = Component(EpicsSignal, "Run")
    width: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Width")


class MeasCompCtr(Device):
    """Measurement Computing USB CTR08 high-speed counter/timer."""

    # https://github.com/epics-modules/measComp/blob/master/measCompApp/Db/measCompDevice.template
    model_name: EpicsSignalRO = Component(EpicsSignalRO, "ModelName", kind="config", string=True)
    model_number: EpicsSignalRO = Component(EpicsSignalRO, "ModelNumber", kind="config")
    firmware_version: EpicsSignalRO = Component(
        EpicsSignalRO, "FirmwareVersion", kind="config", string=True
    )
    unique_id: EpicsSignalRO = Component(EpicsSignalRO, "UniqueID", kind="config", string=True)
    ul_version: EpicsSignalRO = Component(EpicsSignalRO, "ULVersion", kind="config", string=True)
    driver_version: EpicsSignalRO = Component(
        EpicsSignalRO, "DriverVersion", kind="config", string=True
    )
    poll_time_ms: EpicsSignalRO = Component(EpicsSignalRO, "PollTimeMS", kind="config")
    poll_sleep_ms: EpicsSignalRO = Component(EpicsSignalRO, "PollSleepMS", kind="config")
    last_error_message: EpicsSignalRO = Component(
        EpicsSignalRO, "LastErrorMessage", kind="config", string=True
    )

    # https://github.com/epics-modules/measComp/blob/master/measCompApp/Db/USBCTR.substitutions
    long_in: EpicsSignalRO = Component(EpicsSignalRO, "Li")

    binary_in_1: EpicsSignalRO = Component(EpicsSignalRO, "Bi1")
    binary_in_2: EpicsSignalRO = Component(EpicsSignalRO, "Bi2")
    binary_in_3: EpicsSignalRO = Component(EpicsSignalRO, "Bi3")
    binary_in_4: EpicsSignalRO = Component(EpicsSignalRO, "Bi4")
    binary_in_5: EpicsSignalRO = Component(EpicsSignalRO, "Bi5")
    binary_in_6: EpicsSignalRO = Component(EpicsSignalRO, "Bi6")
    binary_in_7: EpicsSignalRO = Component(EpicsSignalRO, "Bi7")
    binary_in_8: EpicsSignalRO = Component(EpicsSignalRO, "Bi8")

    long_out: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Lo")

    binary_out_1: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Bo1")
    binary_out_2: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Bo2")
    binary_out_3: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Bo3")
    binary_out_4: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Bo4")
    binary_out_5: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Bo5")
    binary_out_6: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Bo6")
    binary_out_7: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Bo7")
    binary_out_8: EpicsSignalWithRBV = Component(EpicsSignalWithRBV, "Bo8")

    binary_direction_1: EpicsSignal = Component(EpicsSignal, "Bd1")
    binary_direction_2: EpicsSignal = Component(EpicsSignal, "Bd2")
    binary_direction_3: EpicsSignal = Component(EpicsSignal, "Bd3")
    binary_direction_4: EpicsSignal = Component(EpicsSignal, "Bd4")
    binary_direction_5: EpicsSignal = Component(EpicsSignal, "Bd5")
    binary_direction_6: EpicsSignal = Component(EpicsSignal, "Bd6")
    binary_direction_7: EpicsSignal = Component(EpicsSignal, "Bd7")
    binary_direction_8: EpicsSignal = Component(EpicsSignal, "Bd8")

    pulse_gen_1: MeasCompCtrDevicePulseGenChannel = Component(MeasCompCtrDevicePulseGenChannel, "PulseGen1")
    pulse_gen_2: MeasCompCtrDevicePulseGenChannel = Component(MeasCompCtrDevicePulseGenChannel, "PulseGen2")
    pulse_gen_3: MeasCompCtrDevicePulseGenChannel = Component(MeasCompCtrDevicePulseGenChannel, "PulseGen3")
    pulse_gen_4: MeasCompCtrDevicePulseGenChannel = Component(MeasCompCtrDevicePulseGenChannel, "PulseGen4")

    counter_1: MeasCompCtrDeviceCounterChannel = Component(MeasCompCtrDeviceCounterChannel, "Counter1")
    counter_2: MeasCompCtrDeviceCounterChannel = Component(MeasCompCtrDeviceCounterChannel, "Counter2")
    counter_3: MeasCompCtrDeviceCounterChannel = Component(MeasCompCtrDeviceCounterChannel, "Counter3")
    counter_4: MeasCompCtrDeviceCounterChannel = Component(MeasCompCtrDeviceCounterChannel, "Counter4")
    counter_5: MeasCompCtrDeviceCounterChannel = Component(MeasCompCtrDeviceCounterChannel, "Counter5")
    counter_6: MeasCompCtrDeviceCounterChannel = Component(MeasCompCtrDeviceCounterChannel, "Counter6")
    counter_7: MeasCompCtrDeviceCounterChannel = Component(MeasCompCtrDeviceCounterChannel, "Counter7")
    counter_8: MeasCompCtrDeviceCounterChannel = Component(MeasCompCtrDeviceCounterChannel, "Counter8")
