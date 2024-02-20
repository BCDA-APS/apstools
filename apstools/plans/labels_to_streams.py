"""
Record any labeled objects to streams
+++++++++++++++++++++++++++++++++++++++

To record positions of all motors at the start of a scan, use
``@label_stream_decorator("motor")`` as described next.

EXAMPLE:

.. sidebar::  Ophyd convention

    The ``motor`` label is *singular* by ophyd convention,
    as used in the bluesky ``%wa`` magic.

First, use the ``labels=["motor"]`` keyword when defining your (ophyd) objects.
Here's an example with the ``motor`` label (and others, too) used with various
objects::

    from apstools.plans import label_stream_decorator
    from ophyd import Component, Device, EpicsMotor, EpicsSignal

    class Sample(Device):
        temperature = Component(EpicsSignal, "t2")  # unlabeled
        pressure = Component(EpicsSignal, "ao14")  # unlabeled
        cryo_stream_on = Component(EpicsSignal, "bo27")  # unlabeled
        x = Component(EpicsMotor, "m14", labels=["motor"])
        y = Component(EpicsMotor, "m15", labels=["motor"])

    class Instrument(Device):
        omega = Component(EpicsMotor, "m2", labels=["motor"])
        chi = Component(EpicsMotor, "m3", labels=["motor"])
        phi = Component(EpicsMotor, "m4", labels=["motor"])
        two_theta = Component(EpicsMotor, "m1", labels=["motor"])

        # support table
        x = Component(EpicsMotor, "m7", labels=["motor"])
        y = Component(EpicsMotor, "m8", labels=["motor"])

        sample = Component(Sample, "", labels=["sample"])

    diode = EpicsSignal("ioc:counter2", name="diode", labels=["counter"])
    instrument = Instrument("ioc:", name="instrument")
    m49 = EpicsMotor("ioc:m49", name="m49", labels=["motor"])
    scint = EpicsSignal("ioc:counter1", name="scint", labels=["counter"])

Then define a custom plan with the following (where `when="start"` is the default)::

    @label_stream_decorator("motor")
    def my_count_plan(dets, md=None):
        _md = md or {}
        yield from bp.count(dets, md=_md)

Call this plan with the bluesky RunEngine::

    RE(my_count_plan([scint, diode]))

or from another plan::

    yield from my_count_plan([scint, diode])

Once the run is complete, look for the ``label_start_motor`` stream that has the
positions at the start of the run of all devices with the ``"motor"`` label.  Such as::

    run = cat.v2[-1]  # assume the most recent run
    run.label_start_motor.read()

Similarly, to write the `motor` objects at the end of the run, use the
`when="end"` keyword::

    @label_stream_decorator("motor", when="end")
    def my_count_plan(dets, md=None):
        _md = md or {}
        yield from bp.count(dets, md=_md)

writes a stream named ``label_end_motor`` at the end of the run.  If you want
values record at both *start* and *end*, then use **two** decorators::

    @label_stream_decorator("motor", when="start")
    @label_stream_decorator("motor", when="end")
    def my_count_plan(dets, md=None):
        _md = md or {}
        yield from bp.count(dets, md=_md)

.. autosummary::

   ~label_stream_decorator
   ~label_stream_stub
   ~label_stream_wrapper
   ~When

*new in apstools release 1.6.11*
"""

from enum import Enum

from bluesky import preprocessors as bpp
from bluesky.magics import get_labeled_devices
from bluesky.utils import make_decorator
from bluesky.utils import single_gen

from ..utils import getDefaultNamespace
from .doc_run import write_stream


def label_stream_stub(labels=None, fmt=None, bec=None):
    """
    Writes ophyd-labeled objects to open bluesky run streams. One stream per label.

    PARAMETERS

    labels
        *obj*:
        List of configured ophyd object "labels".
        Default: ``None`` (meaning all).

    fmt
        *str*:
        Format string for stream name(s).
        Default: ``"label_{}"``

    bec
        *obj*:
        Instance of bluesky BestEffortCallback.
        Default: selected from default namespace, if available.

    *new in apstools release 1.6.11*
    """
    from bluesky.callbacks.best_effort import BestEffortCallback

    fmt = fmt or "label_{}"
    ns = getDefaultNamespace()
    devices = get_labeled_devices(ns)
    labels = labels or list(devices.keys())
    if not isinstance(labels, (list, tuple)):
        labels = [labels]
    if bec is None:  # look for bec in default namespace
        for obj in ns.values():
            if isinstance(obj, BestEffortCallback):
                bec = obj
                break

    # fmt: off
    for label in labels:
        if label in devices:
            stream_name = fmt.format(label)
            if bec is not None and stream_name not in bec.noplot_streams:
                bec.noplot_streams.append(stream_name)
            yield from write_stream(
                [pair[-1] for pair in devices[label]],
                stream_name
            )
    # fmt: on


class When(Enum):
    """Describes what point of the run the stream(s) should be written."""

    START = "start"
    END = "end"


def label_stream_wrapper(plan, labels, fmt=None, when="start"):
    """
    Decorator support: Write labeled device(s) to stream(s).  Either at "start" or "end".

    PARAMETERS

    plan
        *obj*:
        Instance of a bluesky plan.
    labels
        *[str]* (or *str*):
        List of configured ophyd object "labels".
        Passed through to :meth:`~apstools.plans.write_label_stream()`.
        Default: ``None`` (meaning all).
    fmt
        *str*:
        Format string for stream name(s).
        Default: ``"label_{when}_{}"``
    when
        *str*:
        Indicates when the stream(s) should be written.  Any of these values:

        =============== ==========================
        value           stream will be written ...
        =============== ==========================
        ``"start"``     just after ``open_run``
        ``"end"``       just before ``close_run``
        ``When.START``  same as ``"start"``
        ``When.END``    same as ``"end"``
        =============== ==========================

        The ``str`` value can be expressed in either upper or lower case.

        Default: ``"start"``

    *new in apstools release 1.6.11*
    """
    try:
        if isinstance(when, str):
            when = When(when.lower())
    except ValueError:
        choices = list(When.__members__.keys())
        raise KeyError(f"Unrecognized value: {when=}, use one of {choices}")

    fmt = fmt or f"label_{when.value}_{{}}"

    def insert_after_open(msg):
        if msg.command == "open_run":

            def new_gen():
                yield from label_stream_stub(labels, fmt=fmt)

            return single_gen(msg), new_gen()
        else:
            return None, None

    def insert_before_close(msg):
        if msg.command == "close_run":

            def new_gen():
                yield from label_stream_stub(labels, fmt=fmt)
                yield msg

            return new_gen(), None
        else:
            return None, None

    action = dict(start=insert_after_open, end=insert_before_close)

    return (yield from bpp.plan_mutator(plan, action[when.value]))


label_stream_decorator = make_decorator(label_stream_wrapper)

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
