"""Test the alignment plans."""

import collections
import math
import time

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

from ...callbacks.scan_signal_statistics import SignalStatsCallback
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
calcs_enable = ophyd.EpicsSignal(f"{IOC_GP}userCalcEnable", name="calcs_enable", string=True)
m1 = ophyd.EpicsMotor(f"{IOC_GP}m1", name="m1")
m2 = ophyd.EpicsMotor(f"{IOC_GP}m2", name="m2")
noisy = ophyd.EpicsSignalRO(f"{IOC_GP}userCalc1.VAL", name="noisy")
scaler1 = ophyd.scaler.ScalerCH(f"{IOC_GP}scaler1", name="scaler1")
swait = SwaitRecord(f"{IOC_GP}userCalc1", name="swait")

for obj in (axis, m1, m2, noisy, scaler1, swait, calcs_enable):
    obj.wait_for_connection()

scaler1.select_channels()

# First, must be connected to m1.
pvoigt = SynPseudoVoigt(name="pvoigt", motor=axis, motor_field=axis.name)
pvoigt.kind = "hinted"
calcs_enable.put("Enable")


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


_TestParameters = collections.namedtuple("TestParameters", "signal mover start finish npts feature")
parms_slower = _TestParameters(noisy, m1, -1.2, 1.2, 11, "max")
parms_faster = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "max")
parms_cen = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "cen")
parms_com = _TestParameters(pvoigt, axis, -1.2, 1.2, 51, "com")


@pytest.mark.parametrize("parms", [parms_slower, parms_faster, parms_cen, parms_com])
def test_direct_implementation_with_rel_scan(parms: _TestParameters):
    RE(bps.mv(parms.mover, 0))
    assert get_position(parms.mover) == 0.0

    if isinstance(parms.signal, SynPseudoVoigt):
        parms.signal.randomize_parameters(scale=250_000)

    RE(bp.rel_scan([parms.signal], parms.mover, parms.start, parms.finish, parms.npts))

    if parms.feature in ("max", "min"):
        center = bec.peaks[parms.feature][parms.signal.name][0]
    else:
        center = bec.peaks[parms.feature][parms.signal.name]
    # fwhm = bec.peaks["fwhm"][signal.name]

    # confirm center will be within scan range
    assert min(parms.start, parms.finish) <= round(center, 8)
    assert center <= max(parms.start, parms.finish)

    RE(bps.mv(parms.mover, center))  # move to the center position
    position = get_position(parms.mover)
    assert math.isclose(position, center, abs_tol=0.001)


_TestParameters = collections.namedtuple("TestParameters", "signals mover start finish npts feature rescan")
parms_motor_slower = _TestParameters(noisy, m1, -1.2, 1.2, 11, "max", True)
parms_ao_faster = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "cen", True)
parms_ao_max = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "max", True)
parms_det_list_of_1 = _TestParameters([pvoigt], axis, -1.2, 1.2, 11, "max", True)
parms_det_list_of_3 = _TestParameters([pvoigt, noisy, scaler1], axis, -1.2, 1.2, 11, "max", True)
parms_det_tuple = _TestParameters((pvoigt), axis, -1.2, 1.2, 11, "max", True)
parms_cen = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "cen", False)
parms_com = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "com", False)
parms_max = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "max", False)
parms_min___pathological = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "min", False)


@pytest.mark.parametrize(
    "parms",
    [
        parms_motor_slower,
        parms_ao_faster,
        parms_ao_max,
        parms_det_list_of_1,
        parms_det_list_of_3,
        parms_det_tuple,
        parms_cen,
        parms_com,
        parms_max,
        parms_min___pathological,
    ],
)
def test_lineup(parms: _TestParameters):
    if isinstance(parms.signals, SynPseudoVoigt):
        parms.signals.randomize_parameters(scale=250_000, bkg=0.000_000_000_1)
    else:
        change_noisy_parameters()

    RE(bps.mv(parms.mover, 0))
    assert get_position(parms.mover) == 0.0

    RE(
        alignment.lineup(
            parms.signals,
            parms.mover,
            parms.start,
            parms.finish,
            parms.npts,
            feature=parms.feature,
            rescan=parms.rescan,
            bec=bec,
        )
    )

    # if parms.rescan and parms.feature in "max cen".split():
    #     # Test if mover position is within width of center.
    #     if isinstance(parms.signals, SynPseudoVoigt):
    #         center = parms.signals.center
    #         width = parms.signals.sigma * 2.355  # FWHM approx.
    #     else:  # FIXME: multiple signals
    #         center = swait.channels.B.input_value.get()
    #         width = swait.channels.C.input_value.get()
    #     # FIXME: fails to find the bec analysis in lineup()
    #     position = get_position(parms.mover)
    #     lo = center-width
    #     hi = center+width
    #     # assert lo <= position <= hi, f"{bec=} {bec.peaks=} {position=} {center=} {width=}"


_TestParameters = collections.namedtuple("TestParameters", "signals, mover, start, finish, npts, feature, nscans")
parms_motor_slower = _TestParameters(noisy, m1, -1.2, 1.2, 11, "max", 2)
parms_ao_faster = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "cen", 2)
parms_ao_max = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "max", 2)
parms_det_list_of_1 = _TestParameters([pvoigt], axis, -1.2, 1.2, 11, "max", 2)
parms_det_list_of_3 = _TestParameters([pvoigt, noisy, scaler1], axis, -1.2, 1.2, 11, "max", 2)
parms_det_tuple = _TestParameters((pvoigt), axis, -1.2, 1.2, 11, "max", 2)
parms_cen = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "cen", 1)
parms_com = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "com", 1)
parms_max = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "max", 1)
parms_min___pathological = _TestParameters(pvoigt, axis, -1.2, 1.2, 11, "min", 1)


@pytest.mark.parametrize(
    "parms",
    [
        parms_motor_slower,
        parms_ao_faster,
        parms_ao_max,
        parms_det_list_of_1,
        parms_det_list_of_3,
        parms_det_tuple,
        parms_cen,
        parms_com,
        parms_max,
        parms_min___pathological,
    ],
)
def test_lineup2(parms: _TestParameters):
    if isinstance(parms.signals, SynPseudoVoigt):
        parms.signals.randomize_parameters(scale=250_000, bkg=0.000_000_000_1)
    else:
        change_noisy_parameters()

    RE(bps.mv(parms.mover, 0))
    assert get_position(parms.mover) == 0.0

    RE(
        alignment.lineup2(
            parms.signals,
            parms.mover,
            parms.start,
            parms.finish,
            parms.npts,
            feature=parms.feature,
            nscans=parms.nscans,
        )
    )


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


_TestParameters = collections.namedtuple(
    "TestParameters", "peak base noise center sigma xlo xhi npts nscans tol outcome"
)
parms_signal_but_high_background = _TestParameters(1e5, 1e6, 10, 0.1, 0.2, -0.7, 0.5, 11, 1, 0.05, False)
parms_model_peak = _TestParameters(1e5, 0, 10, 0.1, 0.2, -0.7, 0.5, 11, 1, 0.05, True)
parms_high_background_poor_resolution = _TestParameters(1e5, 1e4, 10, 0.1, 0.2, -0.7, 0.5, 11, 1, 0.1, True)
parms_not_much_better = _TestParameters(1e5, 1e4, 10, 0.1, 0.2, -0.7, 0.5, 11, 2, 0.05, True)
parms_neg_peak_1x_base = _TestParameters(-1e5, -1e4, 1e-8, 0.1, 0.2, -0.7, 0.5, 11, 1, 0.1, True)
parms_neg_base = _TestParameters(1e5, -10, 10, 0.1, 0.2, -0.7, 0.5, 11, 1, 0.05, True)
parms_small_signal_zero_base = _TestParameters(1e-5, 0, 1e-8, 0.1, 0.2, -0.7, 0.5, 11, 1, 0.05, True)
parms_neg_small_signal_zero_base = _TestParameters(-1e5, 0, 1e-8, 0.1, 0.2, -0.7, 0.5, 11, 1, 0.05, True)
parms_small_signal_finite_base = _TestParameters(1e-5, 1e-7, 1e-8, 0.1, 0.2, -0.7, 0.5, 11, 1, 0.05, True)
parms_no_signal_only_noise = _TestParameters(0, 0, 1e-8, 0.1, 0.2, -1.0, 0.5, 11, 1, 0.05, False)
parms_bkg_plus_noise = _TestParameters(0, 1, 0.1, 0.1, 0.2, -0.7, 0.5, 11, 1, 0.05, False)
parms_bkg_plus_big_noise = _TestParameters(0, 1, 100, 0.1, 0.2, -0.7, 0.5, 11, 1, 0.05, False)
parms_no_signal__ZeroDivisionError = _TestParameters(0, 0, 0, 0.1, 0.2, -0.7, 0.5, 11, 1, 0.005, None)
parms_bkg_only__ZeroDivisionError = _TestParameters(0, 1, 0, 0.1, 0.2, -0.7, 0.5, 11, 1, 0.005, None)


@pytest.mark.parametrize(
    "parms",
    [
        parms_signal_but_high_background,
        parms_model_peak,
        parms_high_background_poor_resolution,
        parms_not_much_better,
        parms_neg_peak_1x_base,
        parms_neg_base,
        parms_small_signal_zero_base,
        parms_neg_small_signal_zero_base,
        parms_small_signal_finite_base,
        parms_no_signal_only_noise,
        parms_bkg_plus_noise,
        parms_bkg_plus_big_noise,
        parms_no_signal__ZeroDivisionError,
        parms_bkg_only__ZeroDivisionError,
    ],
)
def test_lineup2_signal_permutations(parms: _TestParameters):
    starting_position = 0.0
    m1.move(starting_position)
    time.sleep(1)  # without this, the test IOC crashes, sometimes
    swait.reset()
    swait.description.put("CI test lineup2()")
    swait.channels.A.input_pv.put(m1.user_readback.pvname)
    swait.channels.B.input_value.put(parms.center)
    swait.channels.C.input_value.put(parms.sigma)
    swait.channels.D.input_value.put(parms.peak)
    swait.channels.E.input_value.put(parms.base)
    swait.channels.F.input_value.put(parms.noise)
    swait.calculation.put("E+D/(1+((A-B)/C)^2)+F*RNDM")
    swait.scanning_rate.put("I/O Intr")

    stats = SignalStatsCallback()

    detector = noisy
    # fmt: off
    RE(
        alignment.lineup2(
            detector, m1, parms.xlo, parms.xhi, parms.npts, nscans=parms.nscans, signal_stats=stats
        )
    )
    # fmt: on
    change_noisy_parameters()

    try:
        centroid = stats._registers[detector.name].centroid
        if parms.outcome:
            assert math.isclose(m1.position, centroid, abs_tol=parms.tol)
            assert math.isclose(parms.center, centroid, abs_tol=parms.tol)
        else:
            assert not math.isclose(parms.center, centroid, abs_tol=parms.tol)
    except ZeroDivisionError:
        assert math.isclose(m1.position, starting_position, abs_tol=parms.tol)
