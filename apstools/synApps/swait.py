
"""
Ophyd support for the EPICS synApps swait record

EXAMPLES::

    import apstools.synApps
    calcs = apstools.synApps.UserCalcsDevice("xxx:", name="calcs")

    calc1 = calcs.calc1
    apstools.synApps.setup_random_number_swait(calc1)

    apstools.synApps.setup_incrementer_swait(calcs.calc2)
    
    calc1.reset()


.. autosummary::
   
    ~UserCalcsDevice
    ~SwaitRecord
    ~SwaitRecordChannel
    ~setup_random_number_swait 
    ~setup_gaussian_swait
    ~setup_lorentzian_swait 
    ~setup_incrementer_swait

:see: https://htmlpreview.github.io/?https://raw.githubusercontent.com/epics-modules/calc/R3-6-1/documentation/swaitRecord.html
"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2019, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------


from collections import OrderedDict
from ophyd.device import (
    Device,
    Component as Cpt,
    DynamicDeviceComponent as DDC,
    FormattedComponent as FC)
from ophyd import EpicsSignal, Signal
from ophyd.signal import EpicsSignalBase

from ._common import EpicsRecordDeviceCommonAll, EpicsRecordFloatFields
from .. import utils as APS_utils

__all__ = """
    SwaitRecord
    SwaitRecordChannel
    UserCalcsDevice
    setup_random_number_swait 
    setup_gaussian_swait
    setup_lorentzian_swait 
    setup_incrementer_swait
	""".split()

CHANNEL_LETTERS_LIST = "A B C D E F G H I J K L".split()


class SwaitRecordChannel(Device):
    """channel of a synApps swait record: A-L"""

    input_value = FC(EpicsSignal, '{self.prefix}.{self._ch_letter}')
    input_pv = FC(EpicsSignal, '{self.prefix}.IN{self._ch_letter}N')
    input_trigger = FC(EpicsSignal, '{self.prefix}.IN{self._ch_letter}P')
    read_attrs = ['input_value', ]
    hints = {'fields': read_attrs}
    
    def __init__(self, prefix, letter, **kwargs):
        self._ch_letter = letter
        super().__init__(prefix, **kwargs)

    def reset(self):
        """set all fields to default values"""
        self.input_pv.put("")
        self.input_value.put(0)
        self.input_trigger.put("Yes")


def _swait_channels(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        defn[chan] = (SwaitRecordChannel, '', {'letter': chan})
    return defn


class SwaitRecord(EpicsRecordDeviceCommonAll):
    """
    synApps swait record: used as $(P):userCalc$(N)

    .. autosummary::
       
        ~reset

    """
    precision = Cpt(EpicsSignal, ".PREC")
    high_operating_range = Cpt(EpicsSignal, ".HOPR")
    low_operating_range = Cpt(EpicsSignal, ".LOPR")

    calculated_value = Cpt(EpicsSignal, ".VAL")
    calculation = Cpt(EpicsSignal, ".CALC")

    output_link_pv = Cpt(EpicsSignal, '.OUTN')
    output_location_name = Cpt(EpicsSignal, '.DOLN')
    output_location_data = Cpt(EpicsSignal, '.DOLD')
    output_data_option = Cpt(EpicsSignal, ".DOPT")

    output_execute_option = Cpt(EpicsSignal, ".OOPT")
    output_execution_delay = Cpt(EpicsSignal, ".ODLY")
    event_to_issue = Cpt(EpicsSignal, ".OEVT")

    read_attrs = APS_utils.itemizer("channels.%s", CHANNEL_LETTERS_LIST)
    hints = {'fields': read_attrs}
    
    channels = DDC(_swait_channels(CHANNEL_LETTERS_LIST))

    @property
    def value(self):
        return self.calculated_value.value
    
    def reset(self):
        """set all fields to default values"""
        pvname = self.description.pvname.split(".")[0]
        self.description.put(pvname)
        self.scanning_rate.put("Passive")
        self.calculation.put("0")
        self.precision.put("5")
        self.output_location_data.put(0)
        self.output_location_name.put("")
        self.output_data_option.put("Use VAL")
        self.forward_link.put("0")
        self.output_execution_delay.put(0)
        self.output_execute_option.put("Every Time")
        self.output_link_pv.put("")
        for letter in self.channels.read_attrs:
            channel = getattr(self.channels, letter)
            if isinstance(channel, SwaitRecordChannel):
                channel.reset()

        self.read_attrs = ["channels.%s" % c for c in CHANNEL_LETTERS_LIST]
        self.hints = {'fields': self.read_attrs}

        self.read_attrs.append('calculated_value')


class UserCalcsDevice(Device):
    """
    synApps XXX IOC setup of userCalcs: $(P):userCalc$(N)

    .. autosummary::
       
        ~reset

    """

    enable = Cpt(EpicsSignal, 'userCalcEnable')
    calc1 = Cpt(SwaitRecord, 'userCalc1')
    calc2 = Cpt(SwaitRecord, 'userCalc2')
    calc3 = Cpt(SwaitRecord, 'userCalc3')
    calc4 = Cpt(SwaitRecord, 'userCalc4')
    calc5 = Cpt(SwaitRecord, 'userCalc5')
    calc6 = Cpt(SwaitRecord, 'userCalc6')
    calc7 = Cpt(SwaitRecord, 'userCalc7')
    calc8 = Cpt(SwaitRecord, 'userCalc8')
    calc9 = Cpt(SwaitRecord, 'userCalc9')
    calc10 = Cpt(SwaitRecord, 'userCalc10')

    def reset(self):             # lgtm [py/similar-function]
        """set all fields to default values"""
        self.calc1.reset()
        self.calc2.reset()
        self.calc3.reset()
        self.calc4.reset()
        self.calc5.reset()
        self.calc6.reset()
        self.calc7.reset()
        self.calc8.reset()
        self.calc9.reset()
        self.calc10.reset()
        self.read_attrs = ["calc%d" % (c+1) for c in range(10)]


def setup_random_number_swait(swait, **kw):
    """setup swait record to generate random numbers"""
    swait.reset()
    swait.scanning_rate.put("Passive")
    swait.description.put("uniform random numbers")
    swait.calculation.put("RNDM")
    swait.scanning_rate.put(".1 second")

    swait.read_attrs = ['calculated_value',]
    swait.hints = {"fields": swait.read_attrs}


def _setup_peak_swait_(calc, desc, swait, ref_signal, center=0, width=1, scale=1, noise=0.05):
    """
    internal: setup that is common to both Gaussian and Lorentzian swaits
    
    PARAMETERS

    swait : object
        instance of :class:`SwaitRecord`

    ref_signal : object
        instance of :class:`EpicsSignal` used as $A$

    center : float
        $B$, 
        default = 0

    width : float
        $C$,
        default = 1

    scale : float
        $D$,
        default = 1

    noise : float
        $E$,
        default = 0.05
    """
    # consider a noisy background, as well (needs a couple calcs)
    assert(isinstance(swait, SwaitRecord))
    assert(isinstance(ref_signal, EpicsSignalBase))
    assert(width > 0)
    assert(0.0 <= noise <= 1.0)
    swait.reset()
    swait.scanning_rate.put("Passive")
    swait.description.put(desc)
    swait.channels.A.input_pv.put(ref_signal.pvname)
    swait.channels.B.input_value.put(center)
    swait.channels.C.input_value.put(width)
    swait.channels.D.input_value.put(scale)
    swait.channels.E.input_value.put(noise)
    swait.calculation.put(calc)
    swait.scanning_rate.put("I/O Intr")

    swait.read_attrs = ['calculated_value',]
    swait.hints = {"fields": swait.read_attrs}


def setup_gaussian_swait(swait, ref_signal, center=0, width=1, scale=1, noise=0.05):
    """
    setup swait for noisy Gaussian
    
    calculation: $D*(0.95+E*RNDM)/exp(((A-B)/C)^2)$
    
    PARAMETERS

    swait : object
        instance of :class:`SwaitRecord`

    ref_signal : object
        instance of :class:`EpicsSignal` used as $A$

    center : float
        $B$, 
        default = 0

    width : float
        $C$,
        default = 1

    scale : float
        $D$,
        default = 1

    noise : float
        $E$,
        default = 0.05
    """
    _setup_peak_swait_(
        "D*(0.95+E*RNDM)/exp(((A-b)/c)^2)",
        "noisy Gaussian curve", 
        swait, 
        ref_signal, 
        center=center, 
        width=width, 
        scale=scale, 
        noise=noise)


def setup_lorentzian_swait(swait, ref_signal, center=0, width=1, scale=1, noise=0.05):
    """
    setup swait record for noisy Lorentzian
    
    calculation: $D*(0.95+E*RNDM)/(1+((A-B)/C)^2)$
    
    PARAMETERS

    swait : object
        instance of :class:`SwaitRecord`

    ref_signal : object
        instance of :class:`EpicsSignal` used as $A$

    center : float
        $B$, 
        default = 0

    width : float
        $C$,
        default = 1

    scale : float
        $D$,
        default = 1

    noise : float
        $E$,
        default = 0.05
    """
    _setup_peak_swait_(
        "D*(0.95+E*RNDM)/(1+((A-b)/c)^2)", 
        "noisy Lorentzian curve", 
        swait, 
        ref_signal, 
        center=center, 
        width=width, 
        scale=scale, 
        noise=noise)


def setup_incrementer_swait(swait, scan=None, limit=100000):
    """
    setup swait record as an incrementer

    PARAMETERS

    swait : object
        instance of :class:`SwaitRecord`

    scan : text or int or None
        any of the EPICS record `.SCAN` values, 
        or the index number of the value,
        set to default if `None`,
        default: `.1 second`

    limit : int or None
        set the incrementer back to zero 
        when this number is reached (or passed),
        default: 100000

    """
    # consider a noisy background, as well (needs a couple calcs)
    scan = scan or ".1 second"
    swait.reset()
    swait.description.put("incrementer")
    swait.scanning_rate.put("Passive")
    pvname = swait.calculated_value.pvname
    swait.channels.A.input_pv.put(pvname)
    swait.channels.B.input_value.put(limit)
    swait.calculation.put("(A+1) % B")
    swait.precision.put(0)
    swait.scanning_rate.put(scan)

    swait.read_attrs = ['calculated_value',]
    swait.hints = {"fields": swait.read_attrs}
