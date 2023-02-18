"""
Measurement Computing TC-32 Thermocouple reader.
"""

from ophyd import Component
from ophyd import Device
from ophyd import DynamicDeviceComponent as DDC
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd import FormattedComponent as FC

BI_CHANNEL_LIST = [f"Bi{i}" for i in range(8)]
BO_CHANNEL_LIST = [f"Bo{i}" for i in range(32)]  # note Bo31 is not writable
TC_CHANNEL_LIST = [f"Ti{i}" for i in range(32)]


class _MasterDevice(Device):
    def __init__(self, prefix, R, **kwargs):
        self.R = R
        super().__init__(prefix, **kwargs)


class Tc32BinaryInput(_MasterDevice):
    """
    Binary input channel of a MeasComp TC-32 device.

    ``measComp/Db/measCompBinaryIn.template``
    """

    # TODO: are these needed?  {self.prefix}.{self.R}
    bit = FC(EpicsSignalRO, "{self.prefix}{self.R}", kind="hinted")


class Tc32BinaryOutput(_MasterDevice):
    """
    Binary output channel of a MeasComp TC-32 device.

    ``measComp/Db/measCompBinaryOut.template``
    """

    # TODO: are these needed?  {self.prefix}.{self.R}
    bit = FC(EpicsSignalWithRBV, "{self.prefix}.{self.R}", kind="hinted")


class Tc32ThermocoupleChannel(_MasterDevice):
    """
    Thermocouple channel of a MeasComp TC-32 device.

    ``measComp/Db/measCompTemperatureIn.template``
    """

    # TODO: are these needed?  {self.prefix}.{self.R}
    thermocouple_type = FC(EpicsSignal, "{self.prefix}.{self.R}TCType", kind="config")
    filter = FC(EpicsSignal, "{self.prefix}{self.R}Filter", kind="config")
    open_detect = FC(EpicsSignal, "{self.prefix}{self.R}OpenTCDetect", kind="config")
    scale = FC(EpicsSignal, "{self.prefix}{self.R}Scale", kind="config")
    temperature = FC(EpicsSignalRO, "{self.prefix}{self.R}", kind="hinted")


def _channels(dev_class, channel_list):
    # fmt: off
    defn = {
        chan: (dev_class, "", {"R": chan})
        for chan in channel_list
    }
    # fmt: on
    return defn


class MeasCompTc32(Device):
    """
    Measurement Computing TC-32 32-channel Thermocouple reader.
    """

    binary_inputs = DDC(_channels(Tc32BinaryInput, BI_CHANNEL_LIST))
    binary_outputs = DDC(_channels(Tc32BinaryOutput, BO_CHANNEL_LIST))
    thermocouples = DDC(_channels(Tc32ThermocoupleChannel, TC_CHANNEL_LIST))
