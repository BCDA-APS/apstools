#!/usr/bin/env python

"""
demonstrate a BlueSky nscan plan

"""

# Copyright (c) 2017-, UChicago Argonne, LLC.  See LICENSE file.


import logging

from databroker import Broker
# load config from ~/.config/databroker/mongodb_config.yml
db = Broker.named("mongodb_config")

# Make ophyd listen to pyepics.
from ophyd import setup_ophyd
setup_ophyd()

from bluesky import RunEngine
from bluesky.utils import get_history
RE = RunEngine(get_history())
RE.subscribe(db.insert)

# Import matplotlib and put it in interactive mode.
import matplotlib.pyplot as plt
plt.ion()

# Make plots update live while scans run.
from bluesky.utils import install_qt_kicker
install_qt_kicker()

from bluesky.callbacks import LiveTable
from bluesky.plan_tools import print_summary
from ophyd import EpicsMotor

from APS_BlueSky_tools.synApps_ophyd import swaitRecord, swait_setup_random_number
from APS_BlueSky_tools.examples import SynPseudoVoigt
import numpy as np
import socket
from time import sleep

from plans import nscan, TuneAxis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DEMO_SPEC_FILE = "test_specdata.txt"


def main():
    host = socket.gethostname()
    ip = socket.gethostbyname(host)
    if host.find("mintvm") >= 0:
        prefix = "prj:"
    else:
        prefix = "xxx:"
    m1 = EpicsMotor(prefix+"m1", name="m1")
    
    sleep(0.1)  # wait for connect
    starting_position = m1.position
    
    spvoigt = SynPseudoVoigt(
        'spvoigt', m1, 'm1', 
        center=-1.5 + 0.4*np.random.uniform(), 
        eta=0.2 + 0.5*np.random.uniform(), 
        sigma=0.001 + 0.05*np.random.uniform(), 
        scale=1e5,
        bkg=0.01*np.random.uniform())

    tuner = TuneAxis([spvoigt], m1, RE, signal_name="spvoigt")
    live_table = LiveTable(["m1", "spvoigt"])
    RE(tuner.multi_pass_tune(width=2, num=11), live_table)
    print("final: ", tuner.center)
    for stat in tuner.stats:
        print("--", stat.cen, stat.fwhm)

    # repeat but with only one pass
    m1.move(starting_position)
    RE(tuner.tune(2, num=33), live_table)
    print("final: ", tuner.center)
    print("max", tuner.peaks.max)
    print("min", tuner.peaks.min)
    print("centroid", tuner.peaks.cen)
    print("FWHM", tuner.peaks.fwhm)


def main_nscan():
    prefix = "prj:"
    m1 = EpicsMotor(prefix+"m1", name="m1")
    m2 = EpicsMotor(prefix+"m2", name="m2")
    noisy = swaitRecord(prefix+"userCalc1", name="noisy")
    # noisy.read_attrs = ["value"]
    swait_setup_random_number(noisy)
    RE(
        nscan([noisy, ], m1, -1, 0, m2, -2, 0, num=6),
        LiveTable(["m1", "m2", "noisy_val"])
        )


if __name__ == "__main__":
    main()
