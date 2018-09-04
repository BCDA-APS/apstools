
import socket
hostname = socket.gethostname()

if hostname in ('otz.aps.anl.gov',):
    IOC_PREFIX = "gov:"
elif hostname.endswith('jemian.org'):
    IOC_PREFIX = "prj:"
else:
    IOC_PREFIX = "xxx:"


import numpy as np
from ophyd.scaler import ScalerCH
from ophyd import EpicsMotor, Signal, Component, Device
from APS_BlueSky_tools.devices import use_EPICS_scaler_channels, AxisTunerMixin
from bluesky import RunEngine
from bluesky.callbacks.best_effort import BestEffortCallback

from APS_BlueSky_tools.plans import TuneAxis

import datetime
import time
from bluesky.callbacks.fitting import PeakStats
from bluesky import preprocessors as bpp
from bluesky import plan_stubs as bps
from bluesky import plan_patterns as bpat

from bluesky.utils import ts_msg_hook

# Import matplotlib and put it in interactive mode.
import matplotlib.pyplot as plt
plt.ion()

# Make plots update live while scans run.
from bluesky.utils import install_qt_kicker
install_qt_kicker()


RE = RunEngine({})
RE.subscribe(BestEffortCallback())

m1 = EpicsMotor(IOC_PREFIX+"m1", name="m1")
scaler = ScalerCH(IOC_PREFIX+"scaler1", name="scaler")

time.sleep(1)

scaler.match_names()
use_EPICS_scaler_channels(scaler)
for k, v in scaler.read().items():
    print(k, v)
print("scaler.preset_time", scaler.preset_time.value)
# RE.msg_hook = ts_msg_hook


class TunableEpicsMotor(EpicsMotor, AxisTunerMixin):
    pass

 
class MyTuneAxis(TuneAxis): pass
    # override the default tune() method


def myCallback(key, doc):
    if key in (" start", " descriptor", " event", " stop"):
        print("-"*20)
        for k, v in doc.items():
            print("\t", key, k, v)


m1 = TunableEpicsMotor(IOC_PREFIX+"m1", name="m1")
m1.tuner = MyTuneAxis([scaler], m1, signal_name="scint")
m1.tuner.width = 0.02
m1.tuner.num = 21


#RE(bp.count([scaler]))
#RE(bp.scan([scaler], m1, -1, 1, 5))
RE(m1.tune(), myCallback)
