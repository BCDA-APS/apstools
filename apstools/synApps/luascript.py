"""
Ophyd support for the EPICS synApps luascript record

EXAMPLES::

    import apstools.synApps
    scripts = apstools.synApps.UserScriptsDevice("xxx:", name="scripts")
    scripts.reset()

.. autosummary::

    ~UserScriptsDevice
    ~LuascriptRecord
    ~LuascriptRecordNumberInput
    ~LuascriptRecordStringInput

:see: https://epics-lua.readthedocs.io/en/latest/luascriptRecord.html
"""


from collections import OrderedDict

from ophyd import Component as Cpt
from ophyd import Device
from ophyd import DynamicDeviceComponent as DDC
from ophyd import EpicsSignal
from ophyd import FormattedComponent as FC

from .. import utils as APS_utils
from ._common import EpicsRecordDeviceCommonAll

INPUT_LETTERS_LIST = "A B C D E F G H I J".split()


class _LuascriptRecordInputBase(Device):
    """
    (internal): base class for one input of a LuascriptRecord
    """

    # Components must be defined in subclass

    # read_attrs = [
    #     "input_value",
    # ]
    # hints = {"fields": read_attrs}

    def __init__(self, prefix, letter, **kwargs):
        self._ch = letter
        super().__init__(prefix, **kwargs)

    def reset(self):
        """set all fields to default values"""
        raise NotImplementedError("Must define reset() method in subclass.")


class LuascriptRecordNumberInput(_LuascriptRecordInputBase):
    """
    number input of a synApps luascript record: A-J

    .. index:: Ophyd Device; synApps LuascriptRecordNumberInput
    """

    pv_link = FC(EpicsSignal, "{prefix}.INP{_ch}", kind="config", string=True)
    input_value = FC(EpicsSignal, "{prefix}.{_ch}", kind="config")
    description = FC(EpicsSignal, "{prefix}.{_ch}DSC", kind="config", string=True)

    def reset(self):
        """set all fields to default values"""
        self.pv_link.put("")
        self.input_value.put(0)
        self.description.put("")


class LuascriptRecordStringInput(_LuascriptRecordInputBase):
    """
    string input of a synApps luascript record: AA-JJ

    .. index:: Ophyd Device; synApps LuascriptRecordStringInput
    """

    pv_link = FC(EpicsSignal, "{prefix}.IN{_ch}", kind="config", string=True)
    input_value = FC(EpicsSignal, "{prefix}.{_ch}", kind="config", string=True)
    description = FC(EpicsSignal, "{prefix}.{_ch}DN", kind="config", string=True)

    def reset(self):
        """set all fields to default values"""
        self.pv_link.put("")
        self.input_value.put("")
        self.description.put("")


def _inputs(input_list):
    defn = OrderedDict()
    for nsym in input_list:
        defn[nsym] = (LuascriptRecordNumberInput, "", {"letter": nsym})
        ssym = nsym + nsym
        defn[ssym] = (LuascriptRecordStringInput, "", {"letter": ssym})

    return defn


class LuascriptRecord(EpicsRecordDeviceCommonAll):
    """
    EPICS synApps luascript record: used as ``$(P):userScript$(N)``

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
    output_execute_option = Cpt(EpicsSignal, ".OOPT", kind="config")

    error_message = Cpt(EpicsSignal, ".ERR", kind="config", string=True)

    read_attrs = APS_utils.itemizer("inputs.%s", INPUT_LETTERS_LIST)
    hints = {"fields": read_attrs}

    inputs = DDC(_inputs(INPUT_LETTERS_LIST))

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
        new_read_attrs = []
        for letter in self.inputs.read_attrs:
            if "." not in letter:
                input = getattr(self.inputs, letter)
                if isinstance(input, (LuascriptRecordNumberInput, LuascriptRecordStringInput)):
                    new_read_attrs.append(f"inputs.{letter}")
                    input.reset()

        self.read_attrs = new_read_attrs
        self.hints = {"fields": new_read_attrs}

        self.read_attrs.append("number_value")
        self.read_attrs.append("string_value")


class UserScriptsDevice(Device):
    """
    EPICS synApps XXX IOC setup of user lua scripts: ``$(P):userScript$(N)``

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
        enable = self.enable.get()
        self.enable.put("Enable")
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
        self.enable.put(enable)
        self.read_attrs = [f"script{c}" for c in range(10)]


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
