"""
Ophyd support for the EPICS scalcout record

http://htmlpreview.github.io/?https://github.com/epics-modules/calc/blob/R3-6-1/documentation/calcDocs.html

Public Structures

.. autosummary::

    ~UserScalcoutDevice
    ~UserScalcoutN
    ~ScalcoutRecord
    ~ScalcoutRecordNumberChannel
    ~ScalcoutRecordStringChannel
"""

from collections import OrderedDict
from ophyd import Component as Cpt
from ophyd import Device
from ophyd import DynamicDeviceComponent as DDC
from ophyd import EpicsSignal
from ophyd import FormattedComponent as FC

from ._common import EpicsRecordDeviceCommonAll
from ._common import EpicsRecordFloatFields
from ._common import EpicsSynAppsRecordEnableMixin
from .. import utils as APS_utils


CHANNEL_LETTERS_LIST = "A B C D E F G H I J K L".split()


class ScalcoutRecordNumberChannel(Device):
    """
    Number channel of an scalcout record: A-L

    .. index:: Ophyd Device; synApps ScalcoutRecordNumberChannel

    .. autosummary::

        ~reset
    """

    input_value = FC(EpicsSignal, "{prefix}.{_ch}", kind="config")
    input_pv = FC(EpicsSignal, "{prefix}.INP{_ch}", kind="config")

    def __init__(self, prefix, letter, **kwargs):
        self._ch = letter
        super().__init__(prefix, **kwargs)

    def reset(self):
        """set all fields to default values"""
        self.input_pv.put("")
        self.input_value.put(0)


class ScalcoutRecordStringChannel(Device):
    """
    String channel of an scalcout record: AA-LL

    .. index:: Ophyd Device; synApps ScalcoutRecordStringChannel

    .. autosummary::

        ~reset
    """

    input_value = FC(EpicsSignal, "{prefix}.{_ch}", kind="config")
    input_pv = FC(EpicsSignal, "{prefix}.IN{_ch}", kind="config")

    def __init__(self, prefix, letter, **kwargs):
        self._ch = letter
        super().__init__(prefix, **kwargs)

    def reset(self):
        """set all fields to default values"""
        self.input_pv.put("")
        self.input_value.put("")


def _channels(input_list):
    defn = OrderedDict()
    for nsym in input_list:
        defn[nsym] = (ScalcoutRecordNumberChannel, "", {"letter": nsym})
        ssym = nsym + nsym
        defn[ssym] = (ScalcoutRecordStringChannel, "", {"letter": ssym})

    return defn


class ScalcoutRecord(EpicsRecordFloatFields, EpicsRecordDeviceCommonAll):
    """
    EPICS SynApps calc scalcout record support in ophyd

    .. index:: Ophyd Device; synAppsScalcoutRecord

    .. autosummary::

        ~reset

    :see: http://htmlpreview.github.io/?https://github.com/epics-modules/calc/blob/R3-6-1/documentation/calcDocs.html
    """
    units = Cpt(EpicsSignal, ".EGU", kind="config")
    precision = Cpt(EpicsSignal, ".PREC", kind="config")

    calculation = Cpt(EpicsSignal, ".CALC", kind="config", string=True)
    calculated_value = Cpt(EpicsSignal, ".VAL", kind="hinted")
    calculated_value_string = Cpt(EpicsSignal, ".SVAL", kind="normal")

    output_calculation = Cpt(EpicsSignal, ".OCAL", kind="config", string=True)
    output_value = Cpt(EpicsSignal, ".OVAL", kind="config")
    output_value_string = Cpt(EpicsSignal, ".OSV", kind="hinted", string=True)
    output_pv = Cpt(EpicsSignal, ".OUT", kind="config")
    output_execute_option = Cpt(EpicsSignal, ".OOPT", kind="config")
    output_execution_delay = Cpt(EpicsSignal, ".ODLY", kind="config")
    output_data_option = Cpt(EpicsSignal, ".DOPT", kind="config")
    invalid_output_action = Cpt(EpicsSignal, ".IVOA", kind="config")
    invalid_output_value = Cpt(EpicsSignal, ".IVOV", kind="config")
    event_to_issue = Cpt(EpicsSignal, ".OEVT", kind="config")

    output_pv_status = Cpt(EpicsSignal, ".OUTV", kind="config")
    calculation_valid = Cpt(EpicsSignal, ".CLCV", kind="config")
    output_calculation_valid = Cpt(EpicsSignal, ".OCLV", kind="config")
    output_delay_active = Cpt(EpicsSignal, ".DLYA", kind="config")
    wait_for_completion = Cpt(EpicsSignal, ".WAIT", kind="config")

    channels = DDC(_channels(CHANNEL_LETTERS_LIST))

    read_attrs = (
        APS_utils.itemizer("channels.%s", CHANNEL_LETTERS_LIST)
        +
        APS_utils.itemizer("channels.%s", [c+c for c in CHANNEL_LETTERS_LIST])
    )
    hints = {"fields": read_attrs}

    @property
    def value(self):
        return self.calculated_value.get()

    def reset(self):
        """set all fields to default values"""
        pvname = self.description.pvname.split(".")[0]
        self.enable.put("E")
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

        for letter in self.channels.read_attrs:
            channel = getattr(self.channels, letter)
            if isinstance(
                channel,
                (ScalcoutRecordNumberChannel, ScalcoutRecordStringChannel)
            ):
                channel.reset()
        self.read_attrs = (
            ["channels.%s" % c for c in CHANNEL_LETTERS_LIST]
            +
            ["channels.%s" % c+c for c in CHANNEL_LETTERS_LIST]
        )
        self.hints = {"fields": self.read_attrs}


class UserScalcoutN(EpicsSynAppsRecordEnableMixin, ScalcoutRecord):
    """Single instance of the userStringCalcN database."""


class UserScalcoutDevice(Device):
    """
    EPICS synApps XXX IOC setup of user scalcouts: ``$(P):userStringCalc$(N)``

    .. index:: Ophyd Device; synApps UserScalcoutDevice

    .. autosummary::

        ~reset

    """

    enable = Cpt(EpicsSignal, "userStringCalcEnable", kind="omitted")
    scalcout1 = Cpt(UserScalcoutN, "userStringCalc1")
    scalcout2 = Cpt(UserScalcoutN, "userStringCalc2")
    scalcout3 = Cpt(UserScalcoutN, "userStringCalc3")
    scalcout4 = Cpt(UserScalcoutN, "userStringCalc4")
    scalcout5 = Cpt(UserScalcoutN, "userStringCalc5")
    scalcout6 = Cpt(UserScalcoutN, "userStringCalc6")
    scalcout7 = Cpt(UserScalcoutN, "userStringCalc7")
    scalcout8 = Cpt(UserScalcoutN, "userStringCalc8")
    scalcout9 = Cpt(UserScalcoutN, "userStringCalc9")
    scalcout10 = Cpt(UserScalcoutN, "userStringCalc10")

    def reset(self):  # lgtm [py/similar-function]
        """set all fields to default values"""
        self.scalcout1.reset()
        self.scalcout2.reset()
        self.scalcout3.reset()
        self.scalcout4.reset()
        self.scalcout5.reset()
        self.scalcout6.reset()
        self.scalcout7.reset()
        self.scalcout8.reset()
        self.scalcout9.reset()
        self.scalcout10.reset()
        self.read_attrs = ["scalcout%d" % (c + 1) for c in range(10)]
        self.read_attrs.insert(0, "enable")

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
