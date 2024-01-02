"""
LabJack Data Acquisition (DAQ)
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~LabJackBase


Ophyd definitions for Labjack T-series data acquisition devices.

Supported devices, all inherit from ``LabJackBase``:

- T4
- T7
- T7Pro
- T8

These devices are **based on EPICS LabJack module R3.0**. The EPICS IOC
database changed significantly from R2 to R3 when the module was
rewritten to use the LJM library.

.. seealso:: https://github.com/epics-modules/LabJack/releases/tag/R3-0

There are definitions for the entire LabJack device, as well as the
various inputs/outputs available on the LabJack T-series.
Individual inputs can be used as part of other devices. Assuming
analog input 5 is connected to a gas flow meter:

.. code:: python

    from ophyd import Component as Cpt
    from apstools.devices import labjack

    class MyBeamline(Device):
        ...
        gas_flow = Cpt(labjack.AnalogInput, "LabJackT7_1:Ai5")

"""

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import DynamicDeviceComponent as DCpt
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent as FCpt
from ophyd import Kind

from ..synApps import EpicsRecordDeviceCommonAll
from ..synApps import EpicsRecordInputFields
from ..synApps import EpicsRecordOutputFields

__all__ = [
    "AnalogOutput",
    "AnalogInput",
    "DigitalIO",
    "WaveformDigitizer",
    "make_digitizer_waveforms",
    "WaveformGenerator",
    "LabJackBase",
    "LabJackT4",
    "LabJackT7",
    "LabJackT7Pro",
    "LabJackT8",
]

KIND_CONFIG_OR_NORMAL = 3
"""Alternative for ``Kind.config | Kind.normal``."""


class Input(EpicsRecordInputFields, EpicsRecordDeviceCommonAll):
    """A generic input record.

    Similar to synApps input records but with some changes. The .PROC
    field is used as a trigger. This way, even if the .SCAN field is
    set to passive, the record will still update before being read.
    """

    process_record = Cpt(EpicsSignal, ".PROC", kind="omitted", put_complete=True, trigger_value=1)
    final_value = Cpt(EpicsSignalRO, ".VAL", kind="normal", auto_monitor=False)


class Output(EpicsRecordOutputFields, EpicsRecordDeviceCommonAll):
    """A generic output record.

    Intended to be sub-classed into different output types.

    """


class BinaryOutput(Output):

    """A binary input on the labjack.

    Similar to a common EPICS input without the OVAL record.

    """

    output_value = None


class AnalogOutput(Output):
    """An analog output on a labjack device."""


class AnalogInput(Input):
    """An analog input on a labjack device.

    It is based on the synApps input record, but with LabJack specific
    signals added.

    The ``.trigger()`` method will retrieve a fresh value using the
    .PROC field, though based on how EPICS support works, this is
    likely just the most recently polled value from the device. This
    can be useful if the .SCAN field is set to passive.

    """

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


class DigitalIO(Device):
    """A digital input/output channel on the labjack.

    Because of the how the records are structured in EPICS, the prefix
    must not include the "Bi{N}" portion of the prefix. Instead, the
    prefix should be prefix for the whole labjack
    (e.g. ``LabJackT7_1:``), and the channel number should be provided
    using the *ch_num* property. So for the digital I/O with its input
    available at PV ``LabJackT7_1:Bi3``, use:

    .. code:: python

        dio3 = DigitalIO("LabJackT7_1:", name="dio3", ch_num=3)

    This will create signals for the input (``Bi3``), output
    (``Bo3``), and direction (``Bd3``) records.

    """

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
    :py:func:`~apstools.devices.labjack.make_digitizer_waveforms` to
    produce waveform signals based on the number of inputs, using the
    ophyd DynamicDeviceComponent.

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
    """A feature of the Labjack devices that generates output waveforms."""

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


def make_analog_outputs(num_aos: int):
    """Create a dictionary with analog output device definitions.

    For use with an ophyd DynamicDeviceComponent.

    Parameters
    ==========
    num_aos
      How many analog outputs to create.

    """
    defn = {}
    for n in range(num_aos):
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
    defn["dio"] = (EpicsSignalRO, "DIOIn", dict(kind=Kind.normal))
    defn["fio"] = (EpicsSignalRO, "FIOIn", dict(kind=Kind.normal))
    defn["eio"] = (EpicsSignalRO, "EIOIn", dict(kind=Kind.normal))
    defn["cio"] = (EpicsSignalRO, "CIOIn", dict(kind=Kind.normal))
    defn["mio"] = (EpicsSignalRO, "MIOIn", dict(kind=Kind.normal))
    return defn


class LabJackBase(Device):
    """A labjack T-series data acquisition unit (DAQ).

    To use the individual components separately, consider using the
    corresponding devices in the list below.

    This device contains signals for the following:

    - device information (e.g. firmware version ,etc)
    - analog outputs (:py:class:`~apstools.devices.labjack.AnalogInput`)
    - analog inputs* (:py:class:`~apstools.devices.labjack.AnalogOutput`)
    - digital input/output* (:py:class:`~apstools.devices.labjack.DigitalIO`)
    - waveform digitizer* (:py:class:`~apstools.devices.labjack.WaveformDigitizer`)
    - waveform generator (:py:class:`~apstools.devices.labjack.WaveformGenerator`)

    The number of inputs and digital outputs depends on the specific
    LabJack T-series device being used. Therefore, the base device
    ``LabJackBase`` does not implement these I/O signals. Instead,
    consider using one of the subclasses, like ``LabJackT4``.

    The ``.trigger()`` method does not do much. To retrieve fresh
    values for analog inputs where .SCAN is passive, you will need to
    trigger the individual inputs themselves.

    The waveform generator and waveform digitizer are included for
    convenience. Reading all the analog/digital inputs and outputs can
    be done by calling the ``.read()`` method. However, it is unlikely
    that the goal is also to trigger the digitizer and generator
    during this read. For this reason, **the digitizer and generator
    have kind="omitted"**. To trigger the digitizer or generator, they
    can be used as separate devices:

    .. code:: python

        lj = LabJackT4(...)

        # Read a waveform from the digitizer
        lj.waveform_digitizer.trigger().wait()
        lj.waveform_digitizer.read()

        # Same thing for the waveform generator
        lj.waveform_generator.trigger().wait()

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
    analog_outputs = DCpt(make_analog_outputs(2), kind=KIND_CONFIG_OR_NORMAL)
    waveform_generator = Cpt(WaveformGenerator, "", kind=Kind.omitted)


class LabJackT4(LabJackBase):
    # Inherit the docstring from the base class
    # (needed for sphinx auto API)
    __doc__ = LabJackBase.__doc__

    class WaveformDigitizer(WaveformDigitizer):
        waveforms = DCpt(make_digitizer_waveforms(12), kind="normal")

    analog_inputs = DCpt(make_analog_inputs(12), kind=KIND_CONFIG_OR_NORMAL)
    digital_ios = DCpt(make_digital_ios(16), kind=KIND_CONFIG_OR_NORMAL)
    waveform_digitizer = Cpt(WaveformDigitizer, "", kind=Kind.omitted)


class LabJackT7(LabJackBase):
    # Inherit the docstring from the base class
    # (needed for sphinx auto API)
    __doc__ = LabJackBase.__doc__

    class WaveformDigitizer(WaveformDigitizer):
        waveforms = DCpt(make_digitizer_waveforms(14), kind="normal")

    analog_inputs = DCpt(make_analog_inputs(14), kind=KIND_CONFIG_OR_NORMAL)
    digital_ios = DCpt(make_digital_ios(23), kind=KIND_CONFIG_OR_NORMAL)
    waveform_digitizer = Cpt(WaveformDigitizer, "")


class LabJackT7Pro(LabJackBase):
    # Inherit the docstring from the base class
    # (needed for sphinx auto API)
    __doc__ = LabJackBase.__doc__

    class WaveformDigitizer(WaveformDigitizer):
        waveforms = DCpt(make_digitizer_waveforms(14), kind="normal")

    analog_inputs = DCpt(make_analog_inputs(14), kind=KIND_CONFIG_OR_NORMAL)
    digital_ios = DCpt(make_digital_ios(23), kind=KIND_CONFIG_OR_NORMAL)
    waveform_digitizer = Cpt(WaveformDigitizer, "")


class LabJackT8(LabJackBase):
    # Inherit the docstring from the base class
    # (needed for sphinx auto API)
    __doc__ = LabJackBase.__doc__

    class WaveformDigitizer(WaveformDigitizer):
        waveforms = DCpt(make_digitizer_waveforms(8), kind="normal")

    analog_inputs = DCpt(make_analog_inputs(8), kind=KIND_CONFIG_OR_NORMAL)
    digital_ios = DCpt(make_digital_ios(20), kind=KIND_CONFIG_OR_NORMAL)
    waveform_digitizer = Cpt(WaveformDigitizer, "")
