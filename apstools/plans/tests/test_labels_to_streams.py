"""Test recording of labeled objects to streams."""

import bluesky.plan_stubs as bps
import bluesky.plans as bp
import bluesky.preprocessors as bpp
import bluesky.utils
import databroker
import pytest
from bluesky import RunEngine
from bluesky.callbacks import best_effort
from bluesky.magics import get_labeled_devices
from ophyd import EpicsMotor
from ophyd import EpicsSignalRO
from ophyd import Signal

from ...tests import IOC_GP
from ...utils import getDefaultNamespace
from ..doc_run import write_stream
from ..labels_to_streams import label_stream_decorator
from ..labels_to_streams import label_stream_stub
from ..labels_to_streams import label_stream_wrapper

bec = best_effort.BestEffortCallback()
cat = databroker.temp()
RE = RunEngine({})
RE.subscribe(cat.v1.insert)


@pytest.fixture(scope="function")
def m1():
    obj = EpicsMotor(f"{IOC_GP}m1", name="m1", labels=["motor", "positioner"])
    obj.wait_for_connection()

    ns = getDefaultNamespace()
    ns[obj.name] = obj
    yield obj

    ns.pop(obj.name)


@pytest.fixture(scope="function")
def noisy():
    obj = EpicsSignalRO(f"{IOC_GP}userCalc1.VAL", name="noisy", labels=["detector"])
    obj.wait_for_connection()

    ns = getDefaultNamespace()
    ns[obj.name] = obj
    yield obj

    ns.pop(obj.name)


@pytest.fixture(scope="function")
def othersignal():
    obj = Signal(name="othersignal", value=0)  # no labels

    ns = getDefaultNamespace()
    ns[obj.name] = obj
    yield obj

    ns.pop(obj.name)


@pytest.fixture(scope="function")
def simsignal():
    obj = Signal(name="simsignal", value=0, labels=["signal"])

    ns = getDefaultNamespace()
    ns[obj.name] = obj
    yield obj

    ns.pop(obj.name)


def test_empty_namespace_no_exception():
    # no ophyd objects in the namespace
    uids = RE(label_stream_stub())
    # No labels defined, so no streams attempted to write: no exception raised.
    assert len(uids) == 0


def test_call_outside_of_run_engine(noisy):
    ns = getDefaultNamespace()
    assert noisy.name in ns

    # can't record a stream without an open run
    with pytest.raises(bluesky.utils.IllegalMessageSequence) as exinfo:
        RE(label_stream_stub())
    assert "Cannot bundle readings without an open run." in str(exinfo.value)


def test_bad_when(noisy):
    bad_when = "bad_when_value"
    assert label_stream_wrapper(None, None, when=bad_when) is not None  # no exception

    @label_stream_decorator(None, when=bad_when)
    def tester():
        yield from bp.count([noisy])

    with pytest.raises((KeyError, ValueError)) as exinfo:
        RE(tester())
    assert "Unrecognized value:" in str(exinfo.value), f"{exinfo=}"


def test_label_not_found(noisy):
    bad_label = "motors"  # singular is defined
    assert label_stream_wrapper(None, bad_label) is not None  # no exception

    @label_stream_decorator(bad_label)
    def tester():
        yield from bp.count([noisy])

    uids = RE(tester())
    assert len(uids) == 1
    run = cat.v2[uids[-1]]
    assert "primary" in run.metadata["stop"]["num_events"]
    assert f"label_start_{bad_label}" not in run.metadata["stop"]["num_events"]


def test_count_plans(simsignal):
    "Demonstrate that basic count plans run properly."
    # a basic run
    uids = RE(bp.count([simsignal]))
    assert len(uids) == 1
    run = cat.v2[uids[-1]]
    assert "primary" in run.metadata["stop"]["num_events"]

    # same bp.count, but in our own plan

    def my_count(dets):
        yield from bp.count(dets)

    uids = RE(my_count([simsignal]))
    assert len(uids) == 1


def test_labeling(m1, noisy, othersignal, simsignal):
    ns = getDefaultNamespace()
    things = [m1, noisy, simsignal, othersignal]
    for obj in things:
        assert obj.name in ns

    labels = [l for v in things for l in v._ophyd_labels_]
    labels = set(sorted(labels))  # unique list (set, actually) of known labels

    devices = get_labeled_devices(ns)
    for label in labels:
        assert label in devices  # verify label was recognized

    for obj in things:
        for olabel in obj._ophyd_labels_:
            assert olabel in devices
            # verify object is registered by that label
            assert (obj.name, obj) in devices[olabel]


def test_plan_a(m1, noisy, othersignal, simsignal):
    def plan_a(dets, number=3, dwell=0.01, md=None):
        _md = dict(number=number, dwell=dwell)
        _md.update(md or {})

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md=_md)
        def inner():
            yield from label_stream_stub("motor")  # based on ``labels``
            yield from write_stream(noisy, "pre_run")  # by device or signal
            for i in range(number):
                if i > 0:
                    yield from bps.sleep(dwell)
                yield from write_stream(dets, "primary")

        uid = yield from inner()

        return uid

    # same bp.count, but in our own plan
    uids = RE(plan_a([simsignal]))
    assert len(uids) == 1

    run = cat.v2[uids[-1]]
    stream_names = run.metadata["stop"]["num_events"]
    assert len(stream_names) == 3
    assert "primary" in stream_names
    # verify only 1 labeled stream
    assert len([l for l in stream_names if l.startswith("label_")]) == 1

    ds = run.primary.read()
    assert m1.name not in ds
    assert noisy.name not in ds
    assert othersignal.name not in ds
    assert simsignal.name in ds

    assert "label_motor" in stream_names
    ds = run.label_motor.read()
    assert m1.name in ds
    assert noisy.name not in ds
    assert othersignal.name not in ds
    assert simsignal.name not in ds

    assert "pre_run" in stream_names
    ds = run.pre_run.read()
    assert m1.name not in ds
    assert noisy.name in ds
    assert othersignal.name not in ds
    assert simsignal.name not in ds


def test_plan_b(m1, noisy, othersignal, simsignal):
    def plan_b(dets, md=None):
        _md = {}
        _md.update(md or {})

        @bpp.stage_decorator(dets)
        @bpp.run_decorator(md=_md)
        def inner():
            yield from label_stream_stub()  # all labeled objects
            yield from write_stream(dets, "primary")

        uid = yield from inner()

        return uid

    # fmt: off
    labels = set(
        sorted(
            [
                l
                for v in (m1, noisy, simsignal)
                for l in v._ophyd_labels_
            ]
        )
    )
    # fmt: on
    assert len(labels) == 4

    # same bp.count, but in our own plan
    uids = RE(plan_b([othersignal, simsignal]))
    assert len(uids) == 1

    run = cat.v2[uids[-1]]
    stream_names = run.metadata["stop"]["num_events"]
    assert len([l for l in stream_names if l.startswith("label_")]) == len(labels)
    assert len(stream_names) == len(labels) + 1
    for l in labels:
        assert f"label_{l}" in stream_names

    ds = run.primary.read()
    assert m1.name not in ds
    assert noisy.name not in ds
    assert othersignal.name in ds
    assert simsignal.name in ds


def test_decorator(m1, noisy, othersignal, simsignal):
    # by association, tests the label_stream_wrapper
    def the_plan(dets, md=None):
        _md = {}
        _md.update(md or {})

        @label_stream_decorator("motor", when="start")
        @label_stream_decorator("motor", when="end")
        def inner():
            yield from bp.count(dets)

        uid = yield from inner()

        return uid

    uids = RE(the_plan([othersignal, simsignal]))
    assert len(uids) == 1

    run = cat.v2[uids[-1]]
    stream_names = list(run.metadata["stop"]["num_events"].keys())

    for when in "start end".split():
        stream = f"label_{when}_motor"
        assert stream in stream_names

        ds = getattr(run, stream).read().to_dict()

        assert m1.name not in ds
        assert noisy.name not in ds
        assert othersignal.name not in ds
        assert simsignal.name not in ds


def test_as_RE_preprocessor(m1, noisy, othersignal, simsignal):
    def motor_start_preprocessor(plan):
        return label_stream_wrapper(plan, "motor")

    RE = RunEngine({})  # make a new one for testing here
    RE.subscribe(cat.v1.insert)
    RE.preprocessors.append(motor_start_preprocessor)

    dets = [noisy, simsignal]
    uids = RE(bp.count(dets))
    assert len(uids) == 1

    assert "label_start_motor" in cat.v1[-1].stream_names
    assert len(cat.v1[-1].stream_names) == 2
    assert "label_start_motor" in cat.v2[-1]
    assert "primary" in cat.v2[-1]


def test_no_labeled_motor(noisy):
    RE = RunEngine({})  # make a new one for testing here
    RE.subscribe(cat.v1.insert)

    label = "motor"

    @label_stream_decorator(label)
    def tester():
        yield from bp.count([noisy])

    uids = RE(bp.count([noisy]))
    assert len(uids) == 1
    run = cat.v2[uids[-1]]
    assert "primary" in run.metadata["stop"]["num_events"]
    assert f"label_start_{label}" not in run.metadata["stop"]["num_events"]
