"""Ophyd definitions for Labjack T-series data acquisition devices.

Currently this is limited to the Labjack T7.

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
    output = FCpt(Output, "{prefix}Bo{ch_num}")
    direction = FCpt(EpicsSignal, "{prefix}Bd{ch_num}", kind=Kind.config)

    def __init__(self, *args, ch_num, **kwargs):
        self.ch_num = ch_num
        super().__init__(*args, **kwargs)


class LabJackBase(Device):
    """A labjack T-series data acquisition unit (DAQ).

    This device is meant as a base for specific device subclasses. It
    does not have any inputs or outputs.

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
    defn[f"dio"] = (EpicsSignalRO, "DIO", dict(kind=Kind.normal))
    defn[f"fio"] = (EpicsSignalRO, "FIO", dict(kind=Kind.normal))
    defn[f"eio"] = (EpicsSignalRO, "EIO", dict(kind=Kind.normal))
    defn[f"cio"] = (EpicsSignalRO, "CIO", dict(kind=Kind.normal))
    defn[f"mio"] = (EpicsSignalRO, "MIO", dict(kind=Kind.normal))
    return defn


class LabJackT7(LabJackBase):
    analog_inputs = DCpt(make_analog_inputs(14), kind=(Kind.config | Kind.normal))
    analog_outputs = DCpt(make_analog_outputs(2), kind=(Kind.config | Kind.normal))
    digital_ios = DCpt(make_digital_ios(23), kind=(Kind.config | Kind.normal))
