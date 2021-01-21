"""
Ophyd support for the EPICS calcout record

https://wiki-ext.aps.anl.gov/epics/index.php/RRM_3-14_Calcout

Public Structures

.. autosummary::

    ~UserCalcoutDevice
    ~CalcoutRecord
    ~CalcoutRecordChannel
    ~setup_gaussian_calcout
    ~setup_incrementer_calcout
    ~setup_lorentzian_calcout
"""

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2021, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

from collections import OrderedDict
from ophyd.device import (
    Device,
    Component as Cpt,
    DynamicDeviceComponent as DDC,
    FormattedComponent as FC,
)
from ophyd import EpicsSignal, EpicsSignalRO, Signal

from ._common import EpicsRecordDeviceCommonAll, EpicsRecordFloatFields
from .. import utils as APS_utils


__all__ = """
    UserCalcoutDevice
    CalcoutRecord
    CalcoutRecordChannel
    setup_gaussian_calcout
    setup_lorentzian_calcout
    setup_incrementer_calcout
""".split()

CHANNEL_LETTERS_LIST = "A B C D E F G H I J K L".split()


class CalcoutRecordChannel(Device):
    """
    channel of a calcout record: A-L

    .. index:: Ophyd Device; synApps CalcoutRecordChannel

    .. autosummary::

        ~reset
    """

    input_value = FC(EpicsSignal, "{self.prefix}.{self._ch_letter}")
    last_value = FC(EpicsSignalRO, "{self.prefix}.L{self._ch_letter}")
    input_pv = FC(EpicsSignal, "{self.prefix}.INP{self._ch_letter}")
    input_pv_valid = FC(
        EpicsSignalRO, "{self.prefix}.IN{self._ch_letter}V"
    )

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


def _channels(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        defn[chan] = (CalcoutRecordChannel, "", {"letter": chan})
    return defn


class CalcoutRecord(EpicsRecordFloatFields, EpicsRecordDeviceCommonAll):
    """
    EPICS calcout record support in ophyd

    .. index:: Ophyd Device; synApps CalcoutRecord

    .. autosummary::

        ~reset

    :see: https://wiki-ext.aps.anl.gov/epics/index.php/RRM_3-14_Calcout
    """

    units = Cpt(EpicsSignal, ".EGU")
    precision = Cpt(EpicsSignal, ".PREC")

    calculated_value = Cpt(EpicsSignal, ".VAL")
    calculation = Cpt(EpicsSignal, ".CALC")

    output_pv = Cpt(EpicsSignal, ".OUT")
    output_execute_option = Cpt(EpicsSignal, ".OOPT")
    output_execution_delay = Cpt(EpicsSignal, ".ODLY")
    output_data_option = Cpt(EpicsSignal, ".DOPT")
    output_calculation = Cpt(EpicsSignal, ".OCAL")
    output_value = Cpt(EpicsSignal, ".OVAL")
    invalid_output_action = Cpt(EpicsSignal, ".IVOA")
    invalid_output_value = Cpt(EpicsSignal, ".IVOV")
    event_to_issue = Cpt(EpicsSignal, ".OEVT")

    output_pv_status = Cpt(EpicsSignal, ".OUTV")
    calculation_valid = Cpt(EpicsSignal, ".CLCV")
    output_calculation_valid = Cpt(EpicsSignal, ".OCLV")
    output_delay_active = Cpt(EpicsSignal, ".DLYA")

    channels = DDC(_channels(CHANNEL_LETTERS_LIST))

    read_attrs = APS_utils.itemizer("channels.%s", CHANNEL_LETTERS_LIST)
    hints = {"fields": read_attrs}

    @property
    def value(self):
        return self.calculated_value.value

    def reset(self):
        """set all fields to default values"""
        pvname = self.description.pvname.split(".")[0]
        self.scanning_rate.put("Passive")
        self.description.put(pvname)
        self.units.put("")
        self.precision.put("5")

        self.calculation.put("")
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
            if isinstance(channel, CalcoutRecordChannel):
                channel.reset()
        self.hints = {
            "fields": ["channels.%s" % c for c in CHANNEL_LETTERS_LIST]
        }
        self.read_attrs = ["channels.%s" % c for c in CHANNEL_LETTERS_LIST]


class UserCalcoutDevice(Device):
    """
    synApps XXX IOC setup of user calcouts: ``$(P):userCalcOut$(N)``

    .. index:: Ophyd Device; synApps UserCalcoutDevice

    .. autosummary::

        ~reset

    """

    enable = Cpt(EpicsSignal, "userCalcOutEnable")
    calcout1 = Cpt(CalcoutRecord, "userCalcOut1")
    calcout2 = Cpt(CalcoutRecord, "userCalcOut2")
    calcout3 = Cpt(CalcoutRecord, "userCalcOut3")
    calcout4 = Cpt(CalcoutRecord, "userCalcOut4")
    calcout5 = Cpt(CalcoutRecord, "userCalcOut5")
    calcout6 = Cpt(CalcoutRecord, "userCalcOut6")
    calcout7 = Cpt(CalcoutRecord, "userCalcOut7")
    calcout8 = Cpt(CalcoutRecord, "userCalcOut8")
    calcout9 = Cpt(CalcoutRecord, "userCalcOut9")
    calcout10 = Cpt(CalcoutRecord, "userCalcOut10")

    def reset(self):  # lgtm [py/similar-function]
        """set all fields to default values"""
        self.calcout1.reset()
        self.calcout2.reset()
        self.calcout3.reset()
        self.calcout4.reset()
        self.calcout5.reset()
        self.calcout6.reset()
        self.calcout7.reset()
        self.calcout8.reset()
        self.calcout9.reset()
        self.calcout10.reset()
        self.read_attrs = ["calcout%d" % (c + 1) for c in range(10)]
        self.read_attrs.insert(0, "enable")


def _setup_peak_calcout_(
    # fmt: off
    calc, desc, calcout, ref_signal,
    center=0, width=1, scale=1, noise=0.05
    # fmt: on
):
    """
    internal: setup that is common to both Gaussian and Lorentzian calcouts

    PARAMETERS

    calcout
        *object* :
        instance of :class:`CalcoutRecord`

    ref_signal
        *object* :
        instance of :class:`EpicsSignal` used as ``A``

    center
        *float* :
        EPICS record field ``B``,
        default = 0

    width
        *float* :
        EPICS record field ``C``,
        default = 1

    scale
        *float* :
        EPICS record field ``D``,
        default = 1

    noise
        *float* :
        EPICS record field ``E``,
        default = 0.05
    """

    # to add a noisy background will need another calc
    if not isinstance(calcout, CalcoutRecord):
        raise TypeError(
            f"expected CalcoutRecord instance, received {type(calcout)}"
        )
    if not isinstance(ref_signal, Signal):
        raise TypeError(
            f"expected Signal instance, received {type(ref_signal)}"
        )
    if width <= 0:
        raise ValueError(f"width must be positive, received {width}")
    if not (0.0 <= noise <= 1.0):
        raise ValueError(
            f"noise must be between 0 and 1, received {noise}"
        )

    calcout.reset()
    calcout.scanning_rate.put("Passive")
    calcout.description.put(desc)
    calcout.channels.A.input_pv.put(ref_signal.pvname)
    calcout.channels.B.input_value.put(center)
    calcout.channels.C.input_value.put(width)
    calcout.channels.D.input_value.put(scale)
    calcout.channels.E.input_value.put(noise)
    calcout.calculation.put(calc)
    calcout.scanning_rate.put(".1 second")

    calcout.read_attrs = [
        "input_value",
    ]
    calcout.hints = {"fields": calcout.read_attrs}


def setup_gaussian_calcout(
    calcout, ref_signal, center=0, width=1, scale=1, noise=0.05
):
    """
    setup calcout for noisy Gaussian

    calculation::

        D*(0.95+E*RNDM)/exp(((A-B)/C)^2)

    PARAMETERS

    calcout
        *object* :
        instance of :class:`CalcoutRecord`

    ref_signal
        *object* :
        instance of :class:`EpicsSignal` used as ``A``

    center
        *float* :
        EPICS record field ``B``,
        default = 0

    width
        *float* :
        EPICS record field ``C``,
        default = 1

    scale
        *float* :
        EPICS record field ``D``,
        default = 1

    noise
        *float* :
        EPICS record field ``E``,
        default = 0.05
    """
    _setup_peak_calcout_(
        "D*(0.95+E*RNDM)/exp(((A-b)/c)^2)",
        "noisy Gaussian curve",
        calcout,
        ref_signal,
        center=center,
        width=width,
        scale=scale,
        noise=noise,
    )


def setup_lorentzian_calcout(
    calcout, ref_signal, center=0, width=1, scale=1, noise=0.05
):  # lgtm [py/similar-function]
    """
    setup calcout record for noisy Lorentzian

    calculation::

        D*(0.95+E*RNDM)/(1+((A-B)/C)^2)

    PARAMETERS

    calcout
        *object* :
        instance of :class:`CalcoutRecord`

    ref_signal
        *object* :
        instance of :class:`EpicsSignal` used as ``A``

    center
        *float* :
        EPICS record field ``B``,
        default = 0

    width
        *float* :
        EPICS record field ``C``,
        default = 1

    scale
        *float* :
        EPICS record field ``D``,
        default = 1

    noise
        *float* :
        EPICS record field ``E``,
        default = 0.05
    """
    _setup_peak_calcout_(
        "D*(0.95+E*RNDM)/(1+((A-B)/C)^2)",
        "noisy Lorentzian curve",
        calcout,
        ref_signal,
        center=center,
        width=width,
        scale=scale,
        noise=noise,
    )


def setup_incrementer_calcout(calcout, scan=None, limit=100000):
    """
    setup calcout record as an incrementer

    PARAMETERS

    calcout
        *object* :
        instance of :class:`CalcoutRecord`

    scan
        *text* or *int* or ``None`` :
        any of the EPICS record ``.SCAN`` values,
        or the index number of the value,
        set to default if ``None``,
        default: ``.1 second``

    limit
        *int* or ``None`` :
        set the incrementer back to zero
        when this number is reached (or passed),
        default: 100000

    """
    # consider a noisy background, as well (needs a couple calcs)
    scan = scan or ".1 second"
    calcout.reset()
    calcout.scanning_rate.put("Passive")
    calcout.description.put("incrementer")
    pvname = calcout.calculated_value.pvname.split(".")[0]
    calcout.channels.A.input_pv.put(pvname)
    calcout.channels.B.input_value.put(limit)
    calcout.calculation.put("(A+1) % B")
    calcout.scanning_rate.put(scan)

    calcout.hints = {"fields": ["input_value", ]}
    calcout.read_attrs = [
        "input_value",
    ]
