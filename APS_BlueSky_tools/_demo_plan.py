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
from plans import nscan

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DEMO_SPEC_FILE = "test_specdata.txt"


def main():
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
