
"""
(ophyd) Devices that might be useful at the APS using BlueSky

.. autosummary::
   
    ~swaitRecord
    ~swaitRecordChannel
    ~swait_setup_random_number
    ~swait_setup_gaussian
    ~swait_setup_lorentzian
    ~swait_setup_incrementer

"""

# Copyright (c) 2017-, UChicago Argonne, LLC.  See LICENSE file.


from collections import OrderedDict
from ophyd import (
    EpicsSignal,
    EpicsSignalRO,
    EpicsMotor,
    )
from ophyd.device import (
    Device,
    Component as Cpt,
    DynamicDeviceComponent as DDC,
    FormattedComponent as FC,
    )


__all__ = [
    "swaitRecord",
    "swaitRecordChannel",
    "swait_setup_random_number",
    "swait_setup_gaussian",
    "swait_setup_lorentzian",
    "swait_setup_incrementer",
    ]

class swaitRecordChannel(Device):
    """channel of a synApps swait record: A-L"""

    value = FC(EpicsSignal, '{self.prefix}.{self._ch_letter}')
    input_pv = FC(EpicsSignal, '{self.prefix}.IN{self._ch_letter}N')
    input_trigger = FC(EpicsSignal, '{self.prefix}.IN{self._ch_letter}P')
    
    def __init__(self, prefix, letter, **kwargs):
        self._ch_letter = letter
        super().__init__(prefix, **kwargs)


def _swait_channels(attr_fix, id_range):
    defn = OrderedDict()
    for k in id_range:
        #key = '{letter}'.format(letter=k)
        defn[k] = (swaitRecordChannel, '', {'letter': k})
    return defn


class swaitRecord(Device):
    """
    synApps swait record: used as $(P):userCalc$(N)
    
    EXAMPLE
    
    ::
    
        from ophyd import EpicsSignal
        from APS_BlueSky_tools.devices import swaitRecord

        calcs_enable = EpicsSignal("xxx:userCalcEnable", name="calcs_enable")
        calcs_enable.put("Enable")
        calc1 = swaitRecord("xxx:userCalc1", name="calc1")

    """
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
    
    _channel_letters = "A B C D E F G H I J K L".split()
    # TODO: eliminate the ".channels"
    # Note that the scaler support has this also.
    channels = DDC(_swait_channels('chan', _channel_letters))
    
    def reset(self):
        """set all fields to default values"""
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
            channel.value.put(0)
            channel.input_pv.put("")
            channel.input_trigger.put("Yes")


def swait_setup_random_number(swait, **kw):
    """setup swait record to generate random numbers"""
    swait.reset()
    swait.scan.put("Passive")
    swait.calc.put("RNDM")
    swait.scan.put(".1 second")


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
