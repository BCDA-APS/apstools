"""
Measurement Computing TC-32 Thermocouple reader
++++++++++++++++++++++++++++++++++++++++++++++++++

The TC-32 thermocouple module [#]_ is part of the EPICS ``measComp`` [#]_
module.  The module documentation [#]_ shows a GUI screen with basic display of
the 32 thermocouple channels and the various digital (binary) I/O bits.

.. [#] http://www.mccdaq.com/usb-ethernet-data-acquisition/temperature/usb-ethernet-24-bit-thermocouple-daq/TC-32.aspx
.. [#] https://github.com/epics-modules/measComp/tree/master#supported-models
.. [#] https://epics-modules.github.io/measComp/measCompMultiFunctionDoc.html#tc-32

*new in apstools release 1.6.14*

.. rubric:: Public class(es)
.. autosummary::

   ~MeasCompTc32

.. rubric:: Internal class(es)
.. autosummary::

   ~_MC_TC32_BaseClass
   ~Tc32BinaryInput
   ~Tc32BinaryOutput
   ~Tc32ThermocoupleChannel
   ~_channels
"""

from ophyd import Device
from ophyd import DynamicDeviceComponent as DDC
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd import FormattedComponent as FC

BI_CHANNEL_LIST = [f"Bi{i}" for i in range(8)]
BO_CHANNEL_LIST = [f"Bo{i}" for i in range(32)]  # note Bo31 is not writable
TC_CHANNEL_LIST = [f"Ti{i}" for i in range(32)]


class _MC_TC32_BaseClass(Device):
    """
    Base class for I/O interface classes below.

    Enables a common :func:`apstools.devices.measComp_tc32_support._channels()`
    function to work for all the interfaces.

    Users will not need to call this class directly.
    """

    def __init__(self, prefix, R, **kwargs):
        self.R = R
        super().__init__(prefix, **kwargs)


class Tc32BinaryInput(_MC_TC32_BaseClass):
    """
    Binary input channel of a MeasComp TC-32 device.

    * EPICS support: ``measComp/Db/measCompBinaryIn.template``
    * Users will not need to call this class directly.
    """

    bit = FC(EpicsSignalRO, "{self.prefix}{self.R}", kind="hinted")


class Tc32BinaryOutput(_MC_TC32_BaseClass):
    """
    Binary output channel of a MeasComp TC-32 device.

    * EPICS support: ``measComp/Db/measCompBinaryOut.template``
    * Users will not need to call this class directly.
    """

    bit = FC(EpicsSignalWithRBV, "{self.prefix}.{self.R}", kind="hinted")


class Tc32ThermocoupleChannel(_MC_TC32_BaseClass):
    """
    Thermocouple channel of a MeasComp TC-32 device.

    * EPICS support: ``measComp/Db/measCompTemperatureIn.template``
    * Users will not need to call this class directly.
    """

    temperature = FC(EpicsSignalRO, "{self.prefix}{self.R}", kind="hinted")
    filter = FC(EpicsSignal, "{self.prefix}{self.R}Filter", kind="config")
    open_detect = FC(EpicsSignal, "{self.prefix}{self.R}OpenTCDetect", kind="config")
    scale = FC(EpicsSignal, "{self.prefix}{self.R}Scale", kind="config")
    thermocouple_type = FC(EpicsSignal, "{self.prefix}.{self.R}TCType", kind="config")


def _channels(dev_class, channel_list):
    """Create the channels for the I/O interface."""
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
