"""
Ophyd support for the EPICS acalcout record

https://epics-modules.github.io/calc/aCalcoutRecord.html

Public Structures

.. autosummary::

    ~UserArrayCalcDevice
    ~UserArrayCalcN
    ~AcalcoutRecord
    ~AcalcoutArrayRecordChannel
    ~AcalcoutRecordChannel
"""

from collections import OrderedDict

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import DynamicDeviceComponent as DDC
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent as FC

from .. import utils as APS_utils
from ._common import EpicsRecordDeviceCommonAll
from ._common import EpicsRecordFloatFields
from ._common import EpicsSynAppsRecordEnableMixin

CHANNEL_LETTERS_LIST = "A B C D E F G H I J K L".split()


class AcalcoutRecordChannel(Device):
    """
    Float channel of a acalcout record: A-L.

    .. index:: Ophyd Device; synApps AcalcoutRecordChannel

    .. autosummary::

        ~reset
    """

    input_value = FC(EpicsSignal, "{prefix}.{_ch_letter}", kind="config")
    # last_value = FC(EpicsSignalRO, "{prefix}.L{_ch_letter}", kind="config")
    input_pv = FC(EpicsSignal, "{prefix}.INP{_ch_letter}", kind="config")
    input_pv_valid = FC(EpicsSignalRO, "{prefix}.IN{_ch_letter}V", kind="config")

    read_attrs = [
        "input_value",
    ]
    hints = {"fields": read_attrs}

    def __init__(self, prefix, letter, **kwargs):
        self._ch_letter = letter
        super().__init__(prefix, **kwargs)

    def reset(self):
        """set all fields to default values"""
        self.input_pv.put("")
        self.input_value.put(0)


class AcalcoutArrayRecordChannel(Device):
    """
    Array channel of a acalcout record: A-L.

    .. index:: Ophyd Device; synApps AcalcoutArrayRecordChannel

    .. autosummary::

        ~reset
    """

    input_value = FC(EpicsSignal, "{prefix}.{_ch_letters}", kind="config")
    input_pv = FC(EpicsSignal, "{prefix}.IN{_ch_letters}", kind="config")

    read_attrs = [
        "input_value",
    ]
    hints = {"fields": read_attrs}

    def __init__(self, prefix, letter, **kwargs):
        self._ch_letters = letter + letter
        super().__init__(prefix, **kwargs)

    def reset(self):
        """set all fields to default values"""
        self.input_pv.put("")
        self.input_value.put([])


def _channels(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        defn[chan] = (AcalcoutRecordChannel, "", {"letter": chan})
    for chan in channel_list:
        defn[chan + chan] = (AcalcoutArrayRecordChannel, "", {"letter": chan})
    return defn


class AcalcoutRecord(EpicsRecordFloatFields, EpicsRecordDeviceCommonAll):
    """
    EPICS base aCalcout record support in ophyd

    .. index:: Ophyd Device; synApps aCalcout

    .. autosummary::

        ~reset

    :see: https://epics-modules.github.io/calc/aCalcoutRecord.html
    """

    units = Cpt(EpicsSignal, ".EGU", kind="config")
    precision = Cpt(EpicsSignal, ".PREC", kind="config")

    calculated_value = Cpt(EpicsSignal, ".VAL", kind="normal")
    calculated_array = Cpt(EpicsSignalRO, ".AVAL", kind="normal")
    calculation = Cpt(EpicsSignal, ".CALC", kind="config")

    output_pv = Cpt(EpicsSignal, ".OUT", kind="config")
    output_execute_option = Cpt(EpicsSignal, ".OOPT", kind="config")
    output_execution_delay = Cpt(EpicsSignal, ".ODLY", kind="config")
    output_data_option = Cpt(EpicsSignal, ".DOPT", kind="config")
    output_calculation = Cpt(EpicsSignal, ".OCAL", kind="config")
    output_value = Cpt(EpicsSignal, ".OVAL", kind="hinted")
    output_array = Cpt(EpicsSignalRO, ".OAV", kind="hinted")
    invalid_output_action = Cpt(EpicsSignal, ".IVOA", kind="config")
    invalid_output_value = Cpt(EpicsSignal, ".IVOV", kind="config")
    event_to_issue = Cpt(EpicsSignal, ".OEVT", kind="config")

    output_pv_status = Cpt(EpicsSignal, ".OUTV", kind="config")
    calculation_valid = Cpt(EpicsSignal, ".CLCV", kind="config")
    output_calculation_valid = Cpt(EpicsSignal, ".OCLV", kind="config")
    output_delay_active = Cpt(EpicsSignal, ".DLYA", kind="config")

    array_elements_allocated = Cpt(EpicsSignalRO, ".NELM", kind="config")
    array_elements_used = Cpt(EpicsSignal, ".NUSE", kind="config")
    array_size_choice = Cpt(EpicsSignal, ".SIZE", kind="config", string=True)

    channels = DDC(_channels(CHANNEL_LETTERS_LIST))

    read_attrs = APS_utils.itemizer("channels.%s", CHANNEL_LETTERS_LIST)
    hints = {"fields": read_attrs}

    @property
    def value(self):
        return self.calculated_value.get()

    def reset(self):
        """set all fields to default values"""
        pvname = self.description.pvname.split(".")[0]
        self.scanning_rate.put("Passive")
        self.description.put(pvname)
        self.units.put("")
        self.precision.put("5")

        self.calculation.put("0")
        self.calculated_value.put(0)
        self.output_calculation.put("")
        self.output_value.put(0)

        self.forward_link.put("")
        self.output_pv.put("")
        self.invalid_output_action.put(0)
        self.invalid_output_value.put(0)

        self.output_execution_delay.put(0)
        self.output_execute_option.put(0)
        self.output_data_option.put(0)

        self.array_elements_used.put(self.array_elements_allocated.get())
        self.array_size_choice.put("NELM")

        for letter in self.channels.read_attrs:
            channel = getattr(self.channels, letter)
            if isinstance(channel, (AcalcoutRecordChannel, AcalcoutArrayRecordChannel)):
                channel.reset()
        self.hints = {"fields": ["channels.%s" % c for c in CHANNEL_LETTERS_LIST]}
        self.read_attrs = ["channels.%s" % c for c in CHANNEL_LETTERS_LIST]


class UserArrayCalcN(EpicsSynAppsRecordEnableMixin, AcalcoutRecord):
    """Single instance of the userCalcoutN database."""


class UserArrayCalcDevice(Device):
    """
    EPICS synApps XXX IOC setup of user aCalcouts: ``$(P):userArrayCalc$(N)``

    .. index:: Ophyd Device; synApps UserArrayCalcDevice

    .. autosummary::

        ~reset

    """

    enable = Cpt(EpicsSignal, "userArrayCalcEnable", kind="omitted")
    acalcout1 = Cpt(UserArrayCalcN, "userArrayCalc1")
    acalcout2 = Cpt(UserArrayCalcN, "userArrayCalc2")
    acalcout3 = Cpt(UserArrayCalcN, "userArrayCalc3")
    acalcout4 = Cpt(UserArrayCalcN, "userArrayCalc4")
    acalcout5 = Cpt(UserArrayCalcN, "userArrayCalc5")
    acalcout6 = Cpt(UserArrayCalcN, "userArrayCalc6")
    acalcout7 = Cpt(UserArrayCalcN, "userArrayCalc7")
    acalcout8 = Cpt(UserArrayCalcN, "userArrayCalc8")
    acalcout9 = Cpt(UserArrayCalcN, "userArrayCalc9")
    acalcout10 = Cpt(UserArrayCalcN, "userArrayCalc10")

    def reset(self):
        """set all fields to default values"""
        for i in range(10):
            getattr(self, f"acalcout{i+1}").reset()
        self.read_attrs = ["acalcout%d" % (c + 1) for c in range(10)]
        self.read_attrs.insert(0, "enable")


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
