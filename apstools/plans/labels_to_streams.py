"""
Record any labeled objects to streams
+++++++++++++++++++++++++++++++++++++++

Users want to "record all the motor positions at the start of a scan."

TODO: describe/demonstrate such a labeled device

Example:

First, define some objects, some with label assignments::

    from ophyd import Component
    from ophyd import Device
    from ophyd import EpicsMotor
    from ophyd import EpicsSignal

    class Gonio(Device):
        tth = Component(EpicsMotor, "m1", labels=["motor"])
        th = Component(EpicsMotor, "m2", labels=["motor"])
        chi = Component(EpicsMotor, "m3", labels=["motor"])
        phi = Component(EpicsMotor, "m4", labels=["motor"])
        x = Component(EpicsMotor, "m7", labels=["motor"])
        y = Component(EpicsMotor, "m8", labels=["motor"])

    class Sample(Device):
        temperature = Component(EpicsSignal, "t2")  # no labels
        pressure = Component(EpicsSignal, "ao14")  # no labels
        x = Component(EpicsMotor, "m14", labels=["motor"])
        y = Component(EpicsMotor, "m15", labels=["motor"])

    picker = Gonio("ioc:", name="picker")
    sample = Sample("ioc:", name="sample", labels=["sample"])
    m49 = EpicsMotor("ioc:m49", name="m49", labels=["motor"])
    scint = EpicsSignal("ioc:counter1", name="scint", labels=["counter"])
    diode = EpicsSignal("ioc:counter2", name="diode", labels=["counter"])

Then define a custom plan with ...::

    # TODO: once the decorator is ready

    @write_label_stream("motor", when="start")
    def my_count_plan(dets, md=None):
        _md = md or {}
        yield from bp.count(dets, md=_md)

.. autosummary::

   ~write_label_stream

*new in apstools release 1.6.11*
"""

import time

from bluesky import plan_stubs as bps
from bluesky import preprocessors as bpp
from bluesky.magics import get_labeled_devices
from ophyd import Signal

from ..utils import getDefaultNamespace
from .doc_run import addDeviceDataAsStream


def write_label_stream(labels=None, fmt="label_{}"):
    """
    Writes ophyd-labeled objects to bluesky run streams. One stream per label.

    PARAMETERS

    labels *obj*:
        List of configured ophyd object "labels".
        Default: ``None`` (meaning all).

    fmt *str*:
       Format string for stream name(s).
       Default: ``"label_{}"``

    *new in apstools release 1.6.11*
    """
    ns = getDefaultNamespace()
    devices = get_labeled_devices(ns)
    labels = labels or list(devices.keys())
    if not isinstance(labels, (list, tuple)):
        labels = [labels]

    for label in labels:
        # fmt: off
        yield from addDeviceDataAsStream(
            [pair[-1] for pair in devices[label]],
            fmt.format(label)
        )
        # fmt: on


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2023, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
