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

logger = logging.getLogger(__name__)

logger.info(__file__)

from ophyd import Component, Device, EpicsSignal, EpicsSignalRO, EpicsSignalWithRBV


class MeasCompCtrMcs(Device):
    """Measurement Computing USB CTR08 Multi-Channel Scaler Controls."""

    # https://github.com/epics-modules/measComp/blob/master/measCompApp/Db/measCompMCS.template
    absolute_timebase_waveform = Component(EpicsSignal, "AbsTimeWF")
    acquiring = Component(EpicsSignal, "Acquiring", kind="config")
    channel_advance = Component(EpicsSignal, "ChannelAdvance", kind="config")
    client_wait = Component(EpicsSignal, "ClientWait", kind="config")
    current_channel = Component(EpicsSignalRO, "CurrentChannel", kind="omitted")
    do_read_all = Component(EpicsSignal, "DoReadAll", kind="omitted")
    dwell = Component(EpicsSignalWithRBV, "Dwell", kind="config")
    elapsed_real = Component(EpicsSignalRO, "ElapsedReal")
    enable_client_wait = Component(EpicsSignal, "EnableClientWait", kind="config")
    erase_all = Component(EpicsSignal, "EraseAll", kind="omitted")
    erase_start = Component(EpicsSignal, "EraseStart", kind="omitted")
    hardware_acquiring = Component(EpicsSignalRO, "HardwareAcquiring", kind="config")
    max_channels = Component(EpicsSignalRO, "MaxChannels", kind="config")
    mcs_counter_1_enable = Component(EpicsSignal, "MCSCounter1Enable", kind="config")
    mcs_counter_2_enable = Component(EpicsSignal, "MCSCounter2Enable", kind="config")
    mcs_counter_3_enable = Component(EpicsSignal, "MCSCounter3Enable", kind="config")
    mcs_counter_4_enable = Component(EpicsSignal, "MCSCounter4Enable", kind="config")
    mcs_counter_5_enable = Component(EpicsSignal, "MCSCounter5Enable", kind="config")
    mcs_counter_6_enable = Component(EpicsSignal, "MCSCounter6Enable", kind="config")
    mcs_counter_7_enable = Component(EpicsSignal, "MCSCounter7Enable", kind="config")
    mcs_counter_8_enable = Component(EpicsSignal, "MCSCounter8Enable", kind="config")
    mcs_counter_enable = Component(EpicsSignal, "MCSCounterEnable", kind="config")
    mcs_dio_enable = Component(EpicsSignal, "MCSDIOEnable", kind="config")
    model = Component(EpicsSignalRO, "Model", kind="config", string=True)
    n_use_all = Component(EpicsSignal, "NuseAll", kind="omitted")
    point_0_action = Component(EpicsSignal, "Point0Action", kind="config")
    prescale = Component(EpicsSignal, "Prescale", kind="config")
    prescale_counter = Component(EpicsSignal, "PrescaleCounter", kind="config")
    preset_real = Component(EpicsSignal, "PresetReal", kind="config")
    read_all = Component(EpicsSignal, "ReadAll", kind="omitted")
    read_all_once = Component(EpicsSignal, "ReadAllOnce", kind="omitted")
    set_acquiring = Component(EpicsSignal, "SetAcquiring", kind="omitted")
    set_client_wait = Component(EpicsSignal, "SetClientWait", kind="config")
    snl_connected = Component(EpicsSignalRO, "SNL_Connected", kind="config")
    start_all = Component(EpicsSignal, "StartAll", kind="omitted")
    stop_all = Component(EpicsSignal, "StopAll", kind="omitted")
    trigger_mode = Component(EpicsSignal, "TrigMode", kind="config", string=True)

    mca1 = Component(EpicsSignalRO, "mca1", labels=["MCA"])
    mca2 = Component(EpicsSignalRO, "mca2", labels=["MCA"])
    mca3 = Component(EpicsSignalRO, "mca3", labels=["MCA"])
    mca4 = Component(EpicsSignalRO, "mca4", labels=["MCA"])
    mca5 = Component(EpicsSignalRO, "mca5", labels=["MCA"])
    mca6 = Component(EpicsSignalRO, "mca6", labels=["MCA"])
    mca7 = Component(EpicsSignalRO, "mca7", labels=["MCA"])
    mca8 = Component(EpicsSignalRO, "mca8", labels=["MCA"])


class MeasCompCtrDeviceCounterChannel(Device):
    """Measurement Computing USB CTR08 Pulse Counter channel."""

    counts = Component(EpicsSignalRO, "Counts")
    reset = Component(EpicsSignal, "Reset", kind="omitted")


class MeasCompCtrDevicePulseGenChannel(Device):
    """Measurement Computing USB CTR08 Pulse Generator channel."""

    # Do not connect: (calcout) CalcDutyCycle
    # Do not connect: (calcout) CalcFrequency
    # Do not connect: (calcout) CalcPeriod
    # Do not connect: (calcout) CalcWidth
    count = Component(EpicsSignal, "Count")
    delay = Component(EpicsSignalWithRBV, "Delay")
    duty_cycle = Component(EpicsSignalWithRBV, "DutyCycle")
    frequency = Component(EpicsSignalWithRBV, "Frequency")
    idle_state = Component(EpicsSignal, "IdleState")
    period = Component(EpicsSignalWithRBV, "Period")
    run = Component(EpicsSignal, "Run")
    width = Component(EpicsSignalWithRBV, "Width")


class MeasCompCtr(Device):
    """Measurement Computing USB CTR08 high-speed counter/timer."""

    # https://github.com/epics-modules/measComp/blob/master/measCompApp/Db/measCompDevice.template
    model_name = Component(EpicsSignalRO, "ModelName", kind="config", string=True)
    model_number = Component(EpicsSignalRO, "ModelNumber", kind="config")
    firmware_version = Component(
        EpicsSignalRO, "FirmwareVersion", kind="config", string=True
    )
    unique_id = Component(EpicsSignalRO, "UniqueID", kind="config", string=True)
    ul_version = Component(EpicsSignalRO, "ULVersion", kind="config", string=True)
    driver_version = Component(
        EpicsSignalRO, "DriverVersion", kind="config", string=True
    )
    poll_time_ms = Component(EpicsSignalRO, "PollTimeMS", kind="config")
    poll_sleep_ms = Component(EpicsSignalRO, "PollSleepMS", kind="config")
    last_error_message = Component(
        EpicsSignalRO, "LastErrorMessage", kind="config", string=True
    )

    # https://github.com/epics-modules/measComp/blob/master/measCompApp/Db/USBCTR.substitutions
    long_in = Component(EpicsSignalRO, "Li")

    binary_in_1 = Component(EpicsSignalRO, "Bi1")
    binary_in_2 = Component(EpicsSignalRO, "Bi2")
    binary_in_3 = Component(EpicsSignalRO, "Bi3")
    binary_in_4 = Component(EpicsSignalRO, "Bi4")
    binary_in_5 = Component(EpicsSignalRO, "Bi5")
    binary_in_6 = Component(EpicsSignalRO, "Bi6")
    binary_in_7 = Component(EpicsSignalRO, "Bi7")
    binary_in_8 = Component(EpicsSignalRO, "Bi8")

    long_out = Component(EpicsSignalWithRBV, "Lo")

    binary_out_1 = Component(EpicsSignalWithRBV, "Bo1")
    binary_out_2 = Component(EpicsSignalWithRBV, "Bo2")
    binary_out_3 = Component(EpicsSignalWithRBV, "Bo3")
    binary_out_4 = Component(EpicsSignalWithRBV, "Bo4")
    binary_out_5 = Component(EpicsSignalWithRBV, "Bo5")
    binary_out_6 = Component(EpicsSignalWithRBV, "Bo6")
    binary_out_7 = Component(EpicsSignalWithRBV, "Bo7")
    binary_out_8 = Component(EpicsSignalWithRBV, "Bo8")

    binary_direction_1 = Component(EpicsSignal, "Bd1")
    binary_direction_2 = Component(EpicsSignal, "Bd2")
    binary_direction_3 = Component(EpicsSignal, "Bd3")
    binary_direction_4 = Component(EpicsSignal, "Bd4")
    binary_direction_5 = Component(EpicsSignal, "Bd5")
    binary_direction_6 = Component(EpicsSignal, "Bd6")
    binary_direction_7 = Component(EpicsSignal, "Bd7")
    binary_direction_8 = Component(EpicsSignal, "Bd8")

    pulse_gen_1 = Component(MeasCompCtrDevicePulseGenChannel, "PulseGen1")
    pulse_gen_2 = Component(MeasCompCtrDevicePulseGenChannel, "PulseGen2")
    pulse_gen_3 = Component(MeasCompCtrDevicePulseGenChannel, "PulseGen3")
    pulse_gen_4 = Component(MeasCompCtrDevicePulseGenChannel, "PulseGen4")

    counter_1 = Component(MeasCompCtrDeviceCounterChannel, "Counter1")
    counter_2 = Component(MeasCompCtrDeviceCounterChannel, "Counter2")
    counter_3 = Component(MeasCompCtrDeviceCounterChannel, "Counter3")
    counter_4 = Component(MeasCompCtrDeviceCounterChannel, "Counter4")
    counter_5 = Component(MeasCompCtrDeviceCounterChannel, "Counter5")
    counter_6 = Component(MeasCompCtrDeviceCounterChannel, "Counter6")
    counter_7 = Component(MeasCompCtrDeviceCounterChannel, "Counter7")
    counter_8 = Component(MeasCompCtrDeviceCounterChannel, "Counter8")
