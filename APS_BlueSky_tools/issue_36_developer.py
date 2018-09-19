
import numpy as np
import socket
import time

# Import matplotlib and put it in interactive mode.
import matplotlib.pyplot as plt
plt.ion()

from ophyd.scaler import ScalerCH
from ophyd import EpicsMotor, EpicsSignal
from bluesky import RunEngine
from bluesky.callbacks.best_effort import BestEffortCallback
import bluesky.plans as bp 
# Make plots update live while scans run.
from bluesky.utils import install_qt_kicker
install_qt_kicker()

from APS_BlueSky_tools.devices import use_EPICS_scaler_channels, AxisTunerMixin
from APS_BlueSky_tools.plans import TuneAxis
from APS_BlueSky_tools.synApps_ophyd import userCalcsDevice, swait_setup_lorentzian


class TunableEpicsMotor(EpicsMotor, AxisTunerMixin):
    pass

 
class MyTuneAxis(TuneAxis): pass
    # override the default tune() method


def myCallback(key, doc):
    if key in (" start", " descriptor", " event", " stop"):
        print("-"*20)
        for k, v in doc.items():
            print("\t", key, k, v)


def setRandomPeak(calc, motor):
    swait_setup_lorentzian(
        calc, 
        motor, 
        center = -1.5 + 0.5*np.random.uniform(), 
        noise  = 0.2  + 0.2*np.random.uniform(), 
        width  = 0.001 + 0.05*np.random.uniform(), 
        scale  = 1e5,
        )


hostname = socket.gethostname()

HOST_PV_PREFIX_DICT = {
    'otz.aps.anl.gov': "gov:",
    'mint-vm': "prj:",
    'poof': "prj:",
    'enoki': "prj:",
    }
IOC_PREFIX = HOST_PV_PREFIX_DICT.get(hostname, "xxx:")


RE = RunEngine({})
RE.subscribe(BestEffortCallback())

m1 = EpicsMotor(IOC_PREFIX+"m1", name="m1")
scaler = ScalerCH(IOC_PREFIX+"scaler1", name="scaler")
calcs = userCalcsDevice(IOC_PREFIX, name="calcs")

time.sleep(1)
scaler.channels.chan01.chname.put("clock")
scaler.channels.chan02.chname.put("I0")
scaler.channels.chan03.chname.put("scint")
scaler.channels.chan04.chname.put("Jake")
scaler.channels.chan05.chname.put("")
scaler.preset_time.put(0.3)

scaler.match_names()
use_EPICS_scaler_channels(scaler)
for k, v in scaler.read().items():
    print(k, v)
print("scaler.preset_time", scaler.preset_time.value)

# change soft motor resolution from 200 steps/rev to 8000 (steps of 0.00025)
_srev = EpicsSignal(m1.prefix+".SREV", name="_srev")
_srev.put(8000)

m1 = TunableEpicsMotor(IOC_PREFIX+"m1", name="m1")
noisy_calc = calcs.calc1
setRandomPeak(noisy_calc, m1)
noisy = EpicsSignal(noisy_calc.prefix, name="noisy")

m1.tuner = TuneAxis([noisy], m1, signal_name=noisy.name)
# m1.tuner = MyTuneAxis([det], m1, signal_name="det")
m1.tuner.width = 3
m1.tuner.num = 41


#RE(bp.count([scaler]))
#RE(bp.scan([scaler], m1, -1, 1, 5))
RE(m1.tune(), myCallback)
