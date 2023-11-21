"""Ophyd definitions for Labjack T-series data acquisition devices.

Currently this is limited to the Labjack T4, T7, T7-Pro, and T8.

These devices are based on the v3.0.0 EPICS module. The EPICS IOC
database changed significantly from v2 to v3 when the module was
rewritten to use the LJM library.

"""

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import DynamicDeviceComponent as DCpt
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent as FCpt
from ophyd import Kind

from apstools.synApps import EpicsRecordDeviceCommonAll
from apstools.synApps import EpicsRecordInputFields
from apstools.synApps import EpicsRecordOutputFields


class Input(EpicsRecordInputFields, EpicsRecordDeviceCommonAll):
    pass


class Output(EpicsRecordOutputFields, EpicsRecordDeviceCommonAll):
    pass


class BinaryOutput(Output):
    output_value = None


class AnalogInput(Input):
    differential = FCpt(
        EpicsSignal,
        "{self.base_prefix}Diff{self.ch_num}",
        kind=Kind.config,
    )
    high = FCpt(EpicsSignal, "{self.base_prefix}HOPR{self.ch_num}", kind=Kind.config)
    low = FCpt(EpicsSignal, "{self.base_prefix}LOPR{self.ch_num}", kind=Kind.config)
    temperature_units = FCpt(
        EpicsSignal,
        "{self.base_prefix}TempUnits{self.ch_num}",
        kind=Kind.config,
    )
    resolution = FCpt(EpicsSignal, "{self.base_prefix}Resolution{self.ch_num}", kind=Kind.config)
    range = FCpt(
        EpicsSignal,
        "{self.base_prefix}Range{self.ch_num}",
        kind=Kind.config,
    )
    mode = FCpt(EpicsSignal, "{self.base_prefix}Mode{self.ch_num}", kind=Kind.config)
    enable = FCpt(EpicsSignal, "{self.base_prefix}Enable{self.ch_num}", kind=Kind.config)

    @property
    def base_prefix(self):
        return self.prefix.rstrip("0123456789")

    @property
    def ch_num(self):
        return self.prefix[len(self.base_prefix) :]


class AnalogOutput(EpicsRecordOutputFields, EpicsRecordDeviceCommonAll):
    pass


class DigitalIO(Device):
    ch_num: int

    input = FCpt(Input, "{prefix}Bi{ch_num}")
    output = FCpt(BinaryOutput, "{prefix}Bo{ch_num}")
    direction = FCpt(EpicsSignal, "{prefix}Bd{ch_num}", kind=Kind.config)

    def __init__(self, *args, ch_num, **kwargs):
        self.ch_num = ch_num
        super().__init__(*args, **kwargs)


class WaveformDigitizer(Device):
    """A feature of the Labjack devices that allows waveform capture.

    By itself, this device does not include any actual data. It should
    be sub-classed for the individual T-series devices to use
    ``make_digitizer_waveforms`` to produce waveform signals based on
    the number of inputs, using the ophyd DynamicDeviceComponent.

    .. code:: python

        class T7Digitizer(WaveformDigitizer):
            waveforms = DCpt(make_digitizer_waveforms(14), kind="normal")

    """

    num_points = Cpt(EpicsSignal, "WaveDigNumPoints", kind=Kind.config)
    first_chan = Cpt(EpicsSignal, "WaveDigFirstChan", kind=Kind.config)
    num_chans = Cpt(EpicsSignal, "WaveDigNumChans", kind=Kind.config)
    timebase_waveform = Cpt(EpicsSignal, "WaveDigTimeWF", kind=Kind.normal)
    current_point = Cpt(EpicsSignal, "WaveDigCurrentPoint", kind=Kind.omitted)
    dwell = Cpt(EpicsSignal, "WaveDigDwell", kind=Kind.config)
    dwell_actual = Cpt(EpicsSignal, "WaveDigDwellActual", kind=Kind.normal)
    total_time = Cpt(EpicsSignal, "WaveDigTotalTime", kind=Kind.normal)
    resolution = Cpt(EpicsSignal, "WaveDigResolution", kind=Kind.config)
    settling_time = Cpt(EpicsSignal, "WaveDigSettlingTime", kind=Kind.config)
    ext_trigger = Cpt(EpicsSignal, "WaveDigExtTrigger", kind=Kind.omitted)
    ext_clock = Cpt(EpicsSignal, "WaveDigExtClock", kind=Kind.omitted)
    auto_restart = Cpt(EpicsSignal, "WaveDigAutoRestart", kind=Kind.config)
    run = Cpt(EpicsSignal, "WaveDigRun", trigger_value=1, kind=Kind.omitted)
    read_waveform = Cpt(EpicsSignal, "WaveDigReadWF", kind=Kind.omitted)


def make_digitizer_waveforms(num_ais: int):
    """Create a dictionary with volt waveforms for the digitizer.

    For use with an ophyd DynamicDeviceComponent.

    Each analog input on the labjack *could* be included here, and
    probably should be unless there is a specific reason not to.

    Parameters
    ==========
    num_ais
      How many analog inputs to include for this Labjack device.

    """
    defn = {}
    for n in range(num_ais):
        defn[f"wf{n}"] = (EpicsSignalRO, f"WaveDigVoltWF{n}", {})
    return defn


class WaveformGenerator(Device):
    """A feature of the Labjack devices that generates output waveforms.

    By itself, this device does not include any actual data. It should
    be sub-classed for the individual T-series devices to use
    ``make_digitizer_waveforms`` to produce waveform signals based on
    the number of inputs, using the ophyd DynamicDeviceComponent.

    .. code:: python

        class T7Digitizer(WaveformDigitizer):
            waveforms = DCpt(make_digitizer_waveforms(14), kind="normal")

    """
    external_trigger = Cpt(EpicsSignal, "WaveGenExtTrigger", kind=Kind.config)  # config
    external_clock = Cpt(EpicsSignal, "WaveGenExtClock", kind=Kind.config)  # config
    continuous = Cpt(EpicsSignal, "WaveGenContinuous", kind=Kind.config)  # config
    run = Cpt(EpicsSignal, "WaveGenRun", trigger_value=1, kind=Kind.omitted)  # omitted

    # These signals give a readback based on whether user-defined or
    # internal waves are used
    num_points = Cpt(EpicsSignalRO, "WaveGenNumPoints", kind=Kind.config)  # config
    current_point = Cpt(EpicsSignalRO, "WaveGenCurrentPoint", kind=Kind.omitted)  # omitted
    frequency = Cpt(EpicsSignalRO, "WaveGenFrequency", kind=Kind.normal)  # normal
    dwell = Cpt(EpicsSignalRO, "WaveGenDwell", kind=Kind.normal)  # normal
    dwell_actual = Cpt(EpicsSignalRO, "WaveGenDwellActual", kind=Kind.normal)  # normal
    total_time = Cpt(EpicsSignalRO, "WaveGenTotalTime", kind=Kind.normal)  # normal

    # Settings for user-defined waveforms
    user_num_points = Cpt(EpicsSignal, "WaveGenUserNumPoints", kind=Kind.omitted)  # omitted
    user_time_waveform = Cpt(EpicsSignal, "WaveGenUserTimeWF", kind=Kind.normal)  # normal
    user_dwell = Cpt(EpicsSignal, "WaveGenUserDwell", kind=Kind.omitted)  # omitted
    user_frequency = Cpt(EpicsSignal, "WaveGenUserFrequency", kind=Kind.omitted)  # omitted

    # Settings for internal waveforms
    internal_num_points = Cpt(EpicsSignal, "WaveGenIntNumPoints", kind=Kind.omitted)  # omitted
    internal_time_waveform = Cpt(EpicsSignal, "WaveGenIntTimeWF", kind=Kind.normal)  # normal
    internal_dwell = Cpt(EpicsSignal, "WaveGenIntDwell", kind=Kind.omitted)  # omitted
    internal_frequency = Cpt(EpicsSignal, "WaveGenIntFrequency", kind=Kind.omitted)  # omitted
    
    # Waveform specific settings
    user_waveform_0 = Cpt(EpicsSignal, "WaveGenUserWF0", kind=Kind.config)  # config
    internal_waveform_0 = Cpt(EpicsSignalRO, "WaveGenInternalWF0", kind=Kind.omitted)  # omitted
    enable_0 = Cpt(EpicsSignal, "WaveGenEnable0", kind=Kind.config)  # config
    type_0 = Cpt(EpicsSignal, "WaveGenType0", kind=Kind.config)  # config
    pulse_width_0 = Cpt(EpicsSignal, "WaveGenPulseWidth0", kind=Kind.config)  # config
    amplitude_0 = Cpt(EpicsSignal, "WaveGenAmplitude0", kind=Kind.config)  # config
    offset_0 = Cpt(EpicsSignal, "WaveGenOffset0", kind=Kind.config)  # config
    user_waveform_1 = Cpt(EpicsSignal, "WaveGenUserWF1", kind=Kind.config)  # config
    internal_waveform_1 = Cpt(EpicsSignalRO, "WaveGenInternalWF1", kind=Kind.omitted)  # omitted
    enable_1 = Cpt(EpicsSignal, "WaveGenEnable1", kind=Kind.config)  # config
    type_1 = Cpt(EpicsSignal, "WaveGenType1", kind=Kind.config)  # config
    pulse_width_1 = Cpt(EpicsSignal, "WaveGenPulseWidth1", kind=Kind.config)  # config
    amplitude_1 = Cpt(EpicsSignal, "WaveGenAmplitude1", kind=Kind.config)  # config
    offset_1 = Cpt(EpicsSignal, "WaveGenOffset1", kind=Kind.config)  # config
    


def make_analog_inputs(num_ais: int):
    """Create a dictionary with analog input device definitions.

    For use with an ophyd DynamicDeviceComponent.

    Parameters
    ==========
    num_ais
      How many analog inputs to create.

    """
    defn = {}
    for n in range(num_ais):
        defn[f"ai{n}"] = (AnalogInput, f"Ai{n}", {})
    return defn


def make_analog_outputs(num_ais: int):
    """Create a dictionary with analog output device definitions.

    For use with an ophyd DynamicDeviceComponent.

    Parameters
    ==========
    num_aos
      How many analog outputs to create.

    """
    defn = {}
    for n in range(num_ais):
        defn[f"ao{n}"] = (AnalogOutput, f"Ao{n}", {})
    return defn


def make_digital_ios(num_dios: int):
    """Create a dictionary with digital I/O device definitions.

    For use with an ophyd DynamicDeviceComponent.

    Parameters
    ==========
    num_dios
      How many digital I/Os to create.

    """
    defn = {}
    for n in range(num_dios):
        defn[f"dio{n}"] = (DigitalIO, "", dict(ch_num=n))
    # Add the digital word outputs
    defn[f"dio"] = (EpicsSignalRO, "DIOIn", dict(kind=Kind.normal))
    defn[f"fio"] = (EpicsSignalRO, "FIOIn", dict(kind=Kind.normal))
    defn[f"eio"] = (EpicsSignalRO, "EIOIn", dict(kind=Kind.normal))
    defn[f"cio"] = (EpicsSignalRO, "CIOIn", dict(kind=Kind.normal))
    defn[f"mio"] = (EpicsSignalRO, "MIOIn", dict(kind=Kind.normal))
    return defn


class LabJackBase(Device):
    """A labjack T-series data acquisition unit (DAQ).

    """

    model_name = Cpt(EpicsSignal, "ModelName", kind=Kind.config)
    firmware_version = Cpt(EpicsSignal, "FirmwareVersion", kind=Kind.config)
    serial_number = Cpt(EpicsSignal, "SerialNumber", kind=Kind.config)
    device_temperature = Cpt(EpicsSignal, "DeviceTemperature", kind=Kind.config)
    ljm_version = Cpt(EpicsSignal, "LJMVersion", kind=Kind.config)
    driver_version = Cpt(EpicsSignal, "DriverVersion", kind=Kind.config)
    last_error_message = Cpt(EpicsSignal, "LastErrorMessage", kind=Kind.config)
    poll_sleep_ms = Cpt(EpicsSignal, "PollSleepMS", kind=Kind.config)
    poll_time_ms = Cpt(EpicsSignal, "PollTimeMS", kind=Kind.omitted)
    analog_in_settling_time_all = Cpt(EpicsSignal, "AiAllSettlingUS", kind=Kind.config)
    analog_in_resolution_all = Cpt(EpicsSignal, "AiAllResolution", kind=Kind.config)
    analog_in_sampling_rate = Cpt(EpicsSignal, "AiSamplingRate", kind=Kind.config)
    device_reset = Cpt(EpicsSignal, "DeviceReset", kind=Kind.omitted)

    # Common sub-devices (all labjacks have 2 analog outputs)
    # NB: Analog inputs/digital I/Os are on a per-model basis
    analog_outputs = DCpt(make_analog_outputs(2), kind=(Kind.config | Kind.normal))
    waveform_generator = Cpt(WaveformGenerator, "", kind=Kind.omitted)


class LabJackT4(LabJackBase):
    class WaveformDigitizer(WaveformDigitizer):
        waveforms = DCpt(make_digitizer_waveforms(12), kind="normal")

    analog_inputs = DCpt(make_analog_inputs(12), kind=(Kind.config | Kind.normal))
    digital_ios = DCpt(make_digital_ios(16), kind=(Kind.config | Kind.normal))
    waveform_digitizer = Cpt(WaveformDigitizer, "", kind=Kind.omitted)
    

class LabJackT7(LabJackBase):
    class WaveformDigitizer(WaveformDigitizer):
        waveforms = DCpt(make_digitizer_waveforms(14), kind="normal")

    analog_inputs = DCpt(make_analog_inputs(14), kind=(Kind.config | Kind.normal))
    digital_ios = DCpt(make_digital_ios(23), kind=(Kind.config | Kind.normal))
    waveform_digitizer = Cpt(WaveformDigitizer, "")
    
class LabJackT7Pro(LabJackBase):
    class WaveformDigitizer(WaveformDigitizer):
        waveforms = DCpt(make_digitizer_waveforms(14), kind="normal")

    analog_inputs = DCpt(make_analog_inputs(14), kind=(Kind.config | Kind.normal))
    digital_ios = DCpt(make_digital_ios(23), kind=(Kind.config | Kind.normal))
    waveform_digitizer = Cpt(WaveformDigitizer, "")


class LabJackT8(LabJackBase):
    class WaveformDigitizer(WaveformDigitizer):
        waveforms = DCpt(make_digitizer_waveforms(8), kind="normal")

    analog_inputs = DCpt(make_analog_inputs(8), kind=(Kind.config | Kind.normal))
    digital_ios = DCpt(make_digital_ios(20), kind=(Kind.config | Kind.normal))
    waveform_digitizer = Cpt(WaveformDigitizer, "")
    
