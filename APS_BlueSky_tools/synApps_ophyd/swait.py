
"""
Ophyd support for the EPICS synApps swait record

EXAMPLES:;

    import APS_BlueSky_tools.synApps_ophyd
    calcs = APS_BlueSky_tools.synApps_ophyd.userCalcsDevice("xxx:", name="calcs")

    calc1 = calcs.calc1
    APS_BlueSky_tools.synApps_ophyd.swait_setup_random_number(calc1)

    APS_BlueSky_tools.synApps_ophyd.swait_setup_incrementer(calcs.calc2)
    
    calc1.reset()


.. autosummary::
   
    ~swaitRecord 
    ~userCalcsDevice
    ~swait_setup_random_number 
    ~swait_setup_gaussian
    ~swait_setup_lorentzian 
    ~swait_setup_incrementer

"""


from collections import OrderedDict
from ophyd.device import (
    Device,
    Component as Cpt,
    DynamicDeviceComponent as DDC,
    FormattedComponent as FC)
from ophyd import EpicsSignal, EpicsSignalRO, EpicsMotor


__all__ = """
    swaitRecord 
    userCalcsDevice
    swait_setup_random_number 
    swait_setup_gaussian
    swait_setup_lorentzian 
    swait_setup_incrementer
	""".split()


class swaitRecordChannel(Device):
    """channel of a synApps swait record: A-L"""

    value = FC(EpicsSignal, '{self.prefix}.{self._ch_letter}')
    input_pv = FC(EpicsSignal, '{self.prefix}.IN{self._ch_letter}N')
    input_trigger = FC(EpicsSignal, '{self.prefix}.IN{self._ch_letter}P')
    
    def __init__(self, prefix, letter, **kwargs):
        self._ch_letter = letter
        super().__init__(prefix, **kwargs)

    def reset(self):
        """set all fields to default values"""
        self.value.put(0)
        self.input_pv.put("")
        self.input_trigger.put("Yes")


def _swait_channels(channel_list):
    defn = OrderedDict()
    for chan in channel_list:
        defn[chan] = (swaitRecordChannel, '', {'letter': chan})
    return defn


class swaitRecord(Device):
    """synApps swait record: used as $(P):userCalc$(N)"""
    desc = Cpt(EpicsSignal, '.DESC')
    scan = Cpt(EpicsSignal, '.SCAN')
    calc = Cpt(EpicsSignal, '.CALC')
    val = Cpt(EpicsSignalRO, '.VAL')
    prec = Cpt(EpicsSignal, '.PREC')
    oevt = Cpt(EpicsSignal, '.OEVT')
    outn = Cpt(EpicsSignal, '.OUTN')
    odly = Cpt(EpicsSignal, '.ODLY')
    doln = Cpt(EpicsSignal, '.DOLN')
    dold = Cpt(EpicsSignal, '.DOLD')
    dopt = Cpt(EpicsSignal, '.DOPT')
    oopt = Cpt(EpicsSignal, '.OOPT')
    flnk = Cpt(EpicsSignal, '.FLNK')
    
    channels = DDC(
        _swait_channels(
            "A B C D E F G H I J K L".split()
        )
    )
    
    def reset(self):
        """set all fields to default values"""
        self.desc.put(self.desc.pvname.split(".")[0])
        self.scan.put("Passive")
        self.calc.put("0")
        self.prec.put("5")
        self.dold.put(0)
        self.doln.put("")
        self.dopt.put("Use VAL")
        self.flnk.put("0")
        self.odly.put(0)
        self.oopt.put("Every Time")
        self.outn.put("")
        for letter in self.channels.read_attrs:
            channel = self.channels.__getattr__(letter)
            channel.reset()


class userCalcsDevice(Device):
    """synApps XXX IOC setup of userCalcs: $(P):userCalc$(N)"""

    enable = Cpt(EpicsSignal, 'userCalcEnable')
    calc1 = Cpt(swaitRecord, 'userCalc1')
    calc2 = Cpt(swaitRecord, 'userCalc2')
    calc3 = Cpt(swaitRecord, 'userCalc3')
    calc4 = Cpt(swaitRecord, 'userCalc4')
    calc5 = Cpt(swaitRecord, 'userCalc5')
    calc6 = Cpt(swaitRecord, 'userCalc6')
    calc7 = Cpt(swaitRecord, 'userCalc7')
    calc8 = Cpt(swaitRecord, 'userCalc8')
    calc9 = Cpt(swaitRecord, 'userCalc9')
    calc10 = Cpt(swaitRecord, 'userCalc10')

    def reset(self):
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


def swait_setup_random_number(swait, **kw):
    """setup swait record to generate random numbers"""
    swait.reset()
    swait.scan.put("Passive")
    swait.calc.put("RNDM")
    swait.scan.put(".1 second")
    swait.desc.put("uniform random numbers")


def swait_setup_gaussian(swait, motor, center=0, width=1, scale=1, noise=0.05):
    """setup swait for noisy Gaussian"""
    # consider a noisy background, as well (needs a couple calcs)
    assert(isinstance(motor, EpicsMotor))
    assert(width > 0)
    assert(0.0 <= noise <= 1.0)
    swait.reset()
    swait.scan.put("Passive")
    swait.channels.A.input_pv.put(motor.user_readback.pvname)
    swait.channels.B.value.put(center)
    swait.channels.C.value.put(width)
    swait.channels.D.value.put(scale)
    swait.channels.E.value.put(noise)
    swait.calc.put("D*(0.95+E*RNDM)/exp(((A-b)/c)^2)")
    swait.scan.put("I/O Intr")
    swait.desc.put("noisy Gaussian curve")


def swait_setup_lorentzian(swait, motor, center=0, width=1, scale=1, noise=0.05):
    """setup swait record for noisy Lorentzian"""
    # consider a noisy background, as well (needs a couple calcs)
    assert(isinstance(motor, EpicsMotor))
    assert(width > 0)
    assert(0.0 <= noise <= 1.0)
    swait.reset()
    swait.scan.put("Passive")
    swait.channels.A.input_pv.put(motor.user_readback.pvname)
    swait.channels.B.value.put(center)
    swait.channels.C.value.put(width)
    swait.channels.D.value.put(scale)
    swait.channels.E.value.put(noise)
    swait.calc.put("D*(0.95+E*RNDM)/(1+((A-b)/c)^2)")
    swait.scan.put("I/O Intr")
    swait.desc.put("noisy Lorentzian curve")


def swait_setup_incrementer(swait, scan=None, limit=100000):
    """setup swait record as an incrementer"""
    # consider a noisy background, as well (needs a couple calcs)
    scan = scan or ".1 second"
    swait.reset()
    swait.scan.put("Passive")
    pvname = swait.val.pvname.split(".")[0]
    swait.channels.A.input_pv.put(pvname)
    swait.channels.B.value.put(limit)
    swait.calc.put("(A+1) % B")
    swait.scan.put(scan)
    swait.desc.put("incrementer")
