"""
Ophyd support for the EPICS synApps luascript record

EXAMPLES::

    import apstools.synApps
    scripts = apstools.synApps.UserScriptsDevice("xxx:", name="scripts")
    scripts.reset()

.. autosummary::

    ~UserScriptsDevice
    ~LuascriptRecord
    ~LuascriptRecordChannel

:see: https://epics-lua.readthedocs.io/en/latest/luascriptRecord.html
"""


from collections import OrderedDict
from ophyd import Device
from ophyd import Component as Cpt
from ophyd import DynamicDeviceComponent as DDC
from ophyd import FormattedComponent as FC
from ophyd import EpicsSignal

from ._common import EpicsRecordDeviceCommonAll
from .. import utils as APS_utils


CHANNEL_LETTERS_LIST = "A B C D E F G H I J".split()


class LuascriptRecordChannel(Device):
    """
    channel of a synApps luascript record: A-J

    .. index:: Ophyd Device; synApps LuascriptRecordChannel
    """

    number_input_pv = FC(EpicsSignal, "{prefix}.INP{_ch}", kind="config")
    string_input_pv = FC(EpicsSignal, "{prefix}.IN{_ch}{_ch}", kind="config")

    number_input_value = FC(EpicsSignal, "{prefix}.{_ch}", kind="hinted")
    string_input_value = FC(EpicsSignal, "{prefix}.{_ch}{_ch}", kind="hinted")

    number_description = FC(EpicsSignal, "{prefix}.{_ch}DSC", kind="config", string=True)
    string_description = FC(EpicsSignal, "{prefix}.{_ch}{_ch}DN", kind="config", string=True)

    read_attrs = [
        "input_value",
    ]
    hints = {"fields": read_attrs}

    def __init__(self, prefix, letter, **kwargs):
        self._ch = letter
        super().__init__(prefix, **kwargs)

    def reset(self):
        """set all fields to default values"""
        self.number_input_pv.put("")
        self.string_input_pv.put("")
        self.number_input_value.put(0)
        self.string_input_value.put("")
        self.number_description.put("")
        self.string_description.put("")


def _channels(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        defn[chan] = (LuascriptRecordChannel, "", {"letter": chan})
    return defn


class LuascriptRecord(EpicsRecordDeviceCommonAll):
    """
    synApps luascript record: used as ``$(P):userScript$(N)``

    .. index:: Ophyd Device; synApps LuascriptRecord

    .. autosummary::

        ~reset

    """

    precision = Cpt(EpicsSignal, ".PREC", kind="config")

    number_value = Cpt(EpicsSignal, ".VAL", kind="hinted")
    string_value = Cpt(EpicsSignal, ".SVAL", kind="hinted", string=True)
    code = Cpt(EpicsSignal, ".CODE", kind="config", string=True)

    output_link = Cpt(EpicsSignal, ".OUT", kind="config")
    reload_script = Cpt(EpicsSignal, ".RELO", kind="omitted", put_complete=True)

    error_message = Cpt(EpicsSignal, ".ERR", kind="config", string=True)

    read_attrs = APS_utils.itemizer("channels.%s", CHANNEL_LETTERS_LIST)
    hints = {"fields": read_attrs}

    channels = DDC(_channels(CHANNEL_LETTERS_LIST))

    @property
    def value(self):
        return self.calculated_value.get()

    def reset(self):
        """set all fields to default values"""
        pvname = self.description.pvname.split(".")[0]
        self.description.put(pvname)
        self.scanning_rate.put("Passive")
        self.code.put("")
        self.precision.put("5")
        self.output_link.put("")
        self.number_value.put(0)
        self.string_value.put("")
        for letter in self.channels.read_attrs:
            if "." not in letter:
                channel = getattr(self.channels, letter)
                if isinstance(channel, LuascriptRecordChannel):
                    channel.reset()

        self.read_attrs = ["channels.%s" % c for c in CHANNEL_LETTERS_LIST]
        self.hints = {"fields": self.read_attrs}

        self.read_attrs.append("calculated_value")


class UserScriptsDevice(Device):
    """
    synApps XXX IOC setup of userScripts: ``$(P):userScript$(N)``

    .. index:: Ophyd Device; synApps UserScriptsDevice

    .. autosummary::

        ~reset

    """

    enable = Cpt(EpicsSignal, "userScriptEnable", kind="config")
    script0 = Cpt(LuascriptRecord, "userScript0")
    script1 = Cpt(LuascriptRecord, "userScript1")
    script2 = Cpt(LuascriptRecord, "userScript2")
    script3 = Cpt(LuascriptRecord, "userScript3")
    script4 = Cpt(LuascriptRecord, "userScript4")
    script5 = Cpt(LuascriptRecord, "userScript5")
    script6 = Cpt(LuascriptRecord, "userScript6")
    script7 = Cpt(LuascriptRecord, "userScript7")
    script8 = Cpt(LuascriptRecord, "userScript8")
    script9 = Cpt(LuascriptRecord, "userScript9")

    def reset(self):  # lgtm [py/similar-function]
        """set all fields to default values"""
        self.script0.reset()
        self.script1.reset()
        self.script2.reset()
        self.script3.reset()
        self.script4.reset()
        self.script5.reset()
        self.script6.reset()
        self.script7.reset()
        self.script8.reset()
        self.script9.reset()
        self.read_attrs = [f"script{c}" for c in range(10)]

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
