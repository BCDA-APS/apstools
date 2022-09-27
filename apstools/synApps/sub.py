"""
Ophyd support for the EPICS sub record

https://epics.anl.gov/base/R7-0/6-docs/subRecord.html

Public Structures

.. autosummary::

    ~UserAverageN
    ~UserAverageDevice
    ~SubRecord
    ~SubRecordChannel
"""

from collections import OrderedDict
from ophyd import Component as Cpt
from ophyd import Device
from ophyd import DynamicDeviceComponent as DDC
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import FormattedComponent as FC

from ._common import EpicsRecordDeviceCommonAll
from ._common import EpicsRecordFloatFields
from .. import utils as APS_utils


CHANNEL_LETTERS_LIST = "A B C D E F G H I J K L".split()


class SubRecordChannel(Device):
    """
    Number channel of a sub record: A-L

    .. index:: Ophyd Device; synApps SubRecordChannel

    .. autosummary::

        ~reset
    """

    input_value = FC(EpicsSignal, "{prefix}.{_ch}", kind="config")
    input_pv = FC(EpicsSignal, "{prefix}.INP{_ch}", kind="config", string=True)

    def __init__(self, prefix, letter, **kwargs):
        self._ch = letter
        super().__init__(prefix, **kwargs)

    def reset(self):
        """set all fields to default values"""
        self.input_pv.put("")
        self.input_value.put(0)


def _channels(input_list):
    defn = OrderedDict()
    for nsym in input_list:
        defn[nsym] = (SubRecordChannel, "", {"letter": nsym})

    return defn


class SubRecord(EpicsRecordFloatFields, EpicsRecordDeviceCommonAll):
    """
    EPICS base sub record support in ophyd

    .. index:: Ophyd Device; SubRecord

    .. autosummary::

        ~reset

    :see: http://htmlpreview.github.io/?https://github.com/epics-modules/calc/blob/R3-6-1/documentation/calcDocs.html
    """
    units = Cpt(EpicsSignal, ".EGU", kind="config")
    precision = Cpt(EpicsSignal, ".PREC", kind="config")

    calculated_value = Cpt(EpicsSignal, ".VAL", kind="hinted")
    initroutine = Cpt(EpicsSignal, ".INAM", kind="config", string=True)
    subroutine = Cpt(EpicsSignal, ".SNAM", kind="config", string=True)

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

        self.initroutine.put("")  # initSubAve in userAve
        self.subroutine.put("")  # SubAve in userAve
        self.calculated_value.put(0)

        self.forward_link.put("")

        for letter in self.channels.read_attrs:
            channel = getattr(self.channels, letter)
            if isinstance(channel, SubRecordChannel):
                channel.reset()
        self.read_attrs = ["channels.%s" % c for c in CHANNEL_LETTERS_LIST]
        self.hints = {"fields": self.read_attrs}


class UserAverageN(EpicsRecordFloatFields, EpicsRecordDeviceCommonAll):
    """
    EPICS synApps XXX IOC setup of user average: ``$(P):userAve$(N)``

    This database uses a sub record for most features plus additional
    records to support done, acquire, clear, and other features.

    It *uses* a ``sub`` record and other, hence not exactly a :meth:`SubRecord`.
    """
    enable = Cpt(EpicsSignal, "Enable", kind="omitted", string=True, put_complete=True)

    averaged_value = Cpt(EpicsSignalRO, ".VAL", kind="hinted")
    channel = Cpt(EpicsSignal, ".INPB", kind="config", string=True, put_complete=True)

    initroutine = Cpt(EpicsSignalRO, ".INAM", kind="config", string=True)
    subroutine = Cpt(EpicsSignalRO, ".SNAM", kind="config", string=True)

    number_samples = Cpt(EpicsSignal, ".A", kind="config", put_complete=True)
    input_value = Cpt(EpicsSignalRO, ".B", kind="normal")
    current_sample = Cpt(EpicsSignalRO, ".E", kind="config")
    average = Cpt(EpicsSignalRO, ".H", kind="hinted")
    line_fit = Cpt(EpicsSignalRO, ".I", kind="hinted")
    auto = Cpt(EpicsSignalRO, ".J", kind="hinted")
    slope = Cpt(EpicsSignalRO, ".K", kind="hinted")
    corr_coef = Cpt(EpicsSignalRO, ".L", kind="hinted")

    mode = Cpt(EpicsSignal, "_mode", kind="config", string=True, put_complete=True)
    algorithm = Cpt(EpicsSignal, "_algorithm", kind="config", string=True, put_complete=True)

    clear = Cpt(EpicsSignal, ".C", kind="omitted", put_complete=True)
    acquire = Cpt(EpicsSignal, "_acquire", kind="omitted", put_complete=True)
    busy = Cpt(EpicsSignal, "_busy", kind="omitted")

    def reset(self):
        """set all fields to default values"""
        self.enable.put(self.enable.enum_strs[1])  # enable
        pvname = self.description.pvname.split(".")[0]
        self.description.put(pvname)
        for attr in "scanning_rate mode algorithm".split():
            obj = getattr(self, attr)
            obj.put(obj.enum_strs[0])
        self.channel.put("")
        self.number_samples.put(0)
        self.precision.put(0)


class UserAverageDevice(Device):
    """
    EPICS synApps XXX IOC setup of user averaging sub records: ``$(P):userAve$(N)``

    .. index:: Ophyd Device; synApps UserAverageDevice

    .. autosummary::

        ~reset

    """

    enable = Cpt(EpicsSignal, "userAveEnable", kind="omitted")
    average1 = Cpt(UserAverageN, "userAve1")
    average2 = Cpt(UserAverageN, "userAve2")
    average3 = Cpt(UserAverageN, "userAve3")
    average4 = Cpt(UserAverageN, "userAve4")
    average5 = Cpt(UserAverageN, "userAve5")
    average6 = Cpt(UserAverageN, "userAve6")
    average7 = Cpt(UserAverageN, "userAve7")
    average8 = Cpt(UserAverageN, "userAve8")
    average9 = Cpt(UserAverageN, "userAve9")
    average10 = Cpt(UserAverageN, "userAve10")

    def reset(self):  # lgtm [py/similar-function]
        """set all fields to default values"""
        self.average1.reset()
        self.average2.reset()
        self.average3.reset()
        self.average4.reset()
        self.average5.reset()
        self.average6.reset()
        self.average7.reset()
        self.average8.reset()
        self.average9.reset()
        self.average10.reset()
        self.read_attrs = ["average%d" % (c + 1) for c in range(10)]
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
