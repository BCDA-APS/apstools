"""Test the alignment plans."""

import math

import bluesky.plan_stubs as bps
import bluesky.plans as bp
import databroker
import numpy
import ophyd
import pytest
from bluesky import RunEngine
from bluesky.callbacks import best_effort
from ophyd import Component
from ophyd import Device
from ophyd import Signal

from ...devices import SynPseudoVoigt
from ...synApps import SwaitRecord
from ...synApps import setup_lorentzian_swait
from ...tests import IOC_GP
from .. import alignment

bec = best_effort.BestEffortCallback()
cat = databroker.temp()
RE = RunEngine({})
RE.subscribe(cat.v1.insert)
RE.subscribe(bec)
bec.enable_plots()

axis = ophyd.EpicsSignal(f"{IOC_GP}gp:float1", name="axis")
m1 = ophyd.EpicsMotor(f"{IOC_GP}m1", name="m1")
m2 = ophyd.EpicsMotor(f"{IOC_GP}m2", name="m2")
noisy = ophyd.EpicsSignalRO(f"{IOC_GP}userCalc1.VAL", name="noisy")
scaler1 = ophyd.scaler.ScalerCH(f"{IOC_GP}scaler1", name="scaler1")
swait = SwaitRecord(f"{IOC_GP}userCalc1", name="swait")

for obj in (axis, m1, m2, noisy, scaler1, swait):
    obj.wait_for_connection()

scaler1.select_channels()

# First, must be connected to m1.
pvoigt = SynPseudoVoigt(name="pvoigt", motor=axis, motor_field=axis.name)
pvoigt.kind = "hinted"


def change_noisy_parameters(fwhm=0.15, peak=10000, noise=0.08):
    """
    Setup the swait record with new random numbers.
    BLOCKING calls, not a bluesky plan
    """
    swait.reset()
    setup_lorentzian_swait(
        swait,
        m1.user_readback,
        center=2 * numpy.random.random() - 1,
        width=fwhm * numpy.random.random(),
        scale=peak * (9 + numpy.random.random()),
        noise=noise * (0.01 + numpy.random.random()),
    )


def get_position(obj, digits=3):
    if isinstance(obj, ophyd.EpicsMotor):
        position = obj.user_readback.get(use_monitor=False)
    else:
        position = obj.get(use_monitor=False)
    return round(position, digits)


@pytest.mark.parametrize("obj", [axis, m1, noisy, pvoigt, scaler1, swait])
def test_connected(obj):
    assert obj.connected


def test_SynPseudoVoigt_randomize():
    signal = SynPseudoVoigt("signal", axis, axis.name)
    # check default settings
    assert signal.center == 0
    assert signal.eta == 0.5
    assert signal.scale == 1
    assert signal.sigma == 1
    assert signal.bkg == 0
    assert signal.noise is None
    assert signal.noise_multiplier == 1

    signal.randomize_parameters()
    # confirm non-default settings
    assert -1 <= signal.center <= 1
    assert 0.2 <= signal.eta <= 0.7
    assert 95_000 <= signal.scale <= 105_000
    assert 0.001 <= signal.sigma <= 0.051
    assert 0 <= signal.bkg <= 0.01
    assert signal.noise == "poisson"
    assert signal.noise_multiplier == 1


@pytest.mark.parametrize(
    "signal, mover, start, finish, npts, feature",
    [
        [noisy, m1, -1.2, 1.2, 11, "max"],  # slower
        [pvoigt, axis, -1.2, 1.2, 11, "max"],  # faster
        [pvoigt, axis, -1.2, 1.2, 11, "cen"],
        [pvoigt, axis, -1.2, 1.2, 51, "com"],
    ],
)
def test_direct_implementation_with_rel_scan(signal, mover, start, finish, npts, feature):
    RE(bps.mv(mover, 0))
    assert get_position(mover) == 0.0

    if isinstance(signal, SynPseudoVoigt):
        signal.randomize_parameters(scale=250_000)

    RE(bp.rel_scan([signal], mover, start, finish, npts))

    if feature in ("max", "min"):
        center = bec.peaks[feature][signal.name][0]
    else:
        center = bec.peaks[feature][signal.name]
    # fwhm = bec.peaks["fwhm"][signal.name]

    # confirm center will be within scan range
    assert min(start, finish) <= center
    assert center <= max(start, finish)

    RE(bps.mv(mover, center))  # move to the center position
    position = get_position(mover)
    assert math.isclose(position, center, abs_tol=0.001)


@pytest.mark.parametrize(
    "signals, mover, start, finish, npts, feature, rescan",
    [
        [noisy, m1, -1.2, 1.2, 11, "max", True],  # slower, is motor
        [pvoigt, axis, -1.2, 1.2, 11, "cen", True],  # faster, is ao (float)
        [pvoigt, axis, -1.2, 1.2, 11, "max", True],
        [[pvoigt], axis, -1.2, 1.2, 11, "max", True],  # list
        [[pvoigt, noisy, scaler1], axis, -1.2, 1.2, 11, "max", True],  # more than one detector
        [(pvoigt), axis, -1.2, 1.2, 11, "max", True],  # tuple
        [pvoigt, axis, -1.2, 1.2, 11, "cen", False],
        [pvoigt, axis, -1.2, 1.2, 11, "com", False],
        [pvoigt, axis, -1.2, 1.2, 11, "max", False],
        [pvoigt, axis, -1.2, 1.2, 11, "min", False],  # pathological
    ],
)
def test_lineup(signals, mover, start, finish, npts, feature, rescan):
    if isinstance(signals, SynPseudoVoigt):
        signals.randomize_parameters(scale=250_000, bkg=0.000_000_000_1)
    else:
        change_noisy_parameters()

    RE(bps.mv(mover, 0))
    assert get_position(mover) == 0.0

    RE(alignment.lineup(signals, mover, start, finish, npts, feature=feature, rescan=rescan, bec=bec))

    # if rescan and feature in "max cen".split():
    #     # Test if mover position is within width of center.
    #     if isinstance(signals, SynPseudoVoigt):
    #         center = signals.center
    #         width = signals.sigma * 2.355  # FWHM approx.
    #     else:  # FIXME: multiple signals
    #         center = swait.channels.B.input_value.get()
    #         width = swait.channels.C.input_value.get()
    #     # FIXME: fails to find the bec analysis in lineup()
    #     position = get_position(mover)
    #     lo = center-width
    #     hi = center+width
    #     # assert lo <= position <= hi, f"{bec=} {bec.peaks=} {position=} {center=} {width=}"


def test_TuneAxis():
    signal = SynPseudoVoigt(name="signal", motor=m1, motor_field=m1.name)
    signal.kind = "hinted"

    m1.tuner = alignment.TuneAxis([signal], m1)
    assert "tune" in dir(m1.tuner)

    npoints = 9
    uids = RE(m1.tuner.tune(width=4, num=npoints))
    assert len(uids) == 1

    stream_names = cat.v1[uids[-1]].stream_names
    assert ["PeakStats", "primary"] == sorted(stream_names)

    stats = cat.v2[uids[-1]].PeakStats.read()

    expected = dict(  # test a few keys with predictable values
        PeakStats_x=m1.name,
        PeakStats_y=signal.name,
        PeakStats_tune_ok=True,
    )
    for k, exp in expected.items():
        assert k in stats, f"{list(stats.keys())=}"
        v = stats[k].values
        assert v.shape == (1,), f"{v=} {v=} {exp=}"
        assert v[0] == exp, f"{k=} {v=} {exp=}"


def test_tune_axes():
    signal = SynPseudoVoigt(name="signal", motor=m1, motor_field=m1.name)
    signal.kind = "hinted"

    axes = (m1, m2)
    for obj in axes:
        obj.tuner = alignment.TuneAxis([signal], obj)
        assert "tune" in dir(obj.tuner), f"{obj.name=}"

    uids = RE(alignment.tune_axes(axes))
    assert len(uids) == 2


def test_tune_axes_raises():
    signal = SynPseudoVoigt(name="signal", motor=m1, motor_field=m1.name)
    signal.kind = "hinted"

    axes = (m1, m2)
    for obj in axes:
        obj.not_named_tuner = alignment.TuneAxis([signal], obj)
        if "tuner" in dir(obj):  # from other testing here
            del obj.tuner

    with pytest.raises(AttributeError) as exinfo:
        RE(alignment.tune_axes(axes))
    assert f"Did not find '{m1.name}.tuner' attribute." in str(exinfo.value)


def test_TuneResults():
    results = alignment.TuneResults(name="results")
    assert results is not None
    assert results.name == "results"

    assert results.report() is None

    class ImitatorForTesting(Device):
        tune_ok = Component(Signal)
        initial_position = Component(Signal)
        final_position = Component(Signal)
        center = Component(Signal)
        # - - - - -
        x = Component(Signal)
        y = Component(Signal)
        cen = Component(Signal)
        com = Component(Signal)
        fwhm = Component(Signal)
        min = Component(Signal)
        max = Component(Signal)
        crossings = Component(Signal)

    peaks = ImitatorForTesting(name="peaks")
    for k in results.peakstats_attrs:
        if k in "crossings min max".split():
            v = numpy.array([0])
        elif k in "x y".split():
            v = "text"
        else:
            v = 0
        getattr(peaks, k).put(v)
    results.set_stats(peaks)
    assert results.report() is None
