"""Test the alignment plans."""

import warnings
import math
import time
from functools import partial

import bluesky.plan_stubs as bps
import bluesky.plans as bp
import databroker
import numpy
import ophyd
import pytest
import matplotlib
from _pytest.fixtures import FixtureRequest
from bluesky import RunEngine
from bluesky.callbacks import best_effort
from ophyd import Component
from ophyd import Device
from ophyd import Signal

from ...callbacks.scan_signal_statistics import SignalStatsCallback
from ...callbacks.spec_file_writer import SpecWriterCallback2
from ...devices import SynPseudoVoigt
from ...synApps import SwaitRecord
from ...synApps import setup_lorentzian_swait
from ...tests import IOC_GP
from ...tests import in_gha_workflow
from .. import alignment
from ._scaler import ScalerCH


@pytest.fixture(scope="function")
def catalog(RE):
    cat = databroker.temp()
    RE.subscribe(cat.v1.insert)
    return cat


@pytest.fixture(scope="function")
def RE():
    old_backend = matplotlib.get_backend()
    RE_ = RunEngine({})
    # The data we're sending can't fit in constrained figure, but we don't care
    fig_factory = partial(matplotlib.pyplot.figure, constrained_layout=False)
    bec = best_effort.BestEffortCallback(fig_factory=fig_factory)
    RE_.subscribe(bec)
    bec.enable_plots()
    RE_.bec = bec
    try:
        matplotlib.use("agg")
        yield RE_
    finally:
        matplotlib.use(old_backend)


@pytest.fixture(scope="module")
def axis():
    device_ = ophyd.EpicsSignal(f"{IOC_GP}gp:float1", name="axis")
    device_.wait_for_connection()
    return device_


@pytest.fixture(scope="module")
def calcs_enable():
    device_ = ophyd.EpicsSignal(f"{IOC_GP}userCalcEnable", name="calcs_enable", string=True)
    device_.wait_for_connection()
    return device_


@pytest.fixture(scope="module")
def m1():
    device_ = ophyd.EpicsMotor(f"{IOC_GP}m1", name="m1")
    device_.wait_for_connection()
    return device_


@pytest.fixture(scope="module")
def m2():
    device_ = ophyd.EpicsMotor(f"{IOC_GP}m2", name="m2")
    device_.wait_for_connection()
    return device_


@pytest.fixture(scope="module")
def noisy():
    device_ = ophyd.EpicsSignalRO(f"{IOC_GP}userCalc1.VAL", name="noisy")
    device_.wait_for_connection()
    return device_


@pytest.fixture(scope="module")
def scaler1():
    device_ = ScalerCH(f"{IOC_GP}scaler1", name="scaler1")
    device_.wait_for_connection()
    device_.select_channels()
    return device_


@pytest.fixture(scope="module")
def swait():
    device_ = SwaitRecord(f"{IOC_GP}userCalc1", name="swait")
    device_.wait_for_connection()
    return device_


@pytest.fixture(scope="module")
def I0(scaler1, noisy):
    device_ = scaler1.channels.chan02.s
    device_.parent.override_signal = noisy
    return device_


@pytest.fixture()
def simulated_mover():
    return Signal(name="simulated_mover", value=0.0)


@pytest.fixture(scope="module")
def epics_pvoigt(axis, calcs_enable):
    axis.wait_for_connection()
    calcs_enable.wait_for_connection()
    device_ = SynPseudoVoigt(name="epics_pvoigt", motor=axis, motor_field=axis.name)
    device_.kind = "hinted"
    calcs_enable.put("Enable")
    return device_


@pytest.fixture()
def simulated_pvoigt(simulated_mover):
    device_ = SynPseudoVoigt(
        name="simulated_pvoigt",
        motor=simulated_mover,
        motor_field=simulated_mover.name,
        center=0.1,
        scale=250_000,
        sigma=0.2,
        bkg=0,
        noise="poisson",
    )
    device_.kind = "hinted"
    return device_


def change_noisy_parameters(swait, motor, fwhm=0.15, peak=10000, noise=0.08):
    """
    Setup the swait record with new random numbers.
    BLOCKING calls, not a bluesky plan
    """
    swait.reset()
    setup_lorentzian_swait(
        swait,
        motor.user_readback,
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


@pytest.mark.iocs
@pytest.mark.parametrize("device_name", ["axis", "m1", "noisy", "epics_pvoigt", "scaler1", "swait"])
def test_connected(device_name, request: FixtureRequest):
    device = request.getfixturevalue(device_name)
    assert device.connected


@pytest.mark.iocs
def test_SynPseudoVoigt_randomize(axis):
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


@pytest.mark.iocs
@pytest.mark.parametrize(
    "parms",
    [
        pytest.param(
            dict(signal="noisy", mover="m1", start=-1.2, finish=1.2, npts=11, feature="max"),
            id="epics-noisy-max",
        ),
        pytest.param(
            dict(signal="epics_pvoigt", mover="axis", start=-1.2, finish=1.2, npts=11, feature="max"),
            id="epics-pseudo-voigt-max",
        ),
        pytest.param(
            dict(signal="epics_pvoigt", mover="axis", start=-1.2, finish=1.2, npts=11, feature="cen"),
            id="epics-pseudo-voigt-centroid",
        ),
        pytest.param(
            dict(signal="epics_pvoigt", mover="axis", start=-1.2, finish=1.2, npts=51, feature="com"),
            id="epics-pseudo-voigt-center-of-mass",
        ),
    ],
)
def test_direct_implementation_with_rel_scan(parms, RE: RunEngine, request: FixtureRequest):
    bec = RE.bec
    mover = request.getfixturevalue(parms["mover"])
    signal = request.getfixturevalue(parms["signal"])
    RE(bps.mv(mover, 0))
    assert get_position(mover) == 0.0

    if isinstance(signal, SynPseudoVoigt):
        signal.randomize_parameters(scale=250_000)

    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", "invalid value encountered in scalar divide")
        RE(bp.rel_scan([signal], mover, parms["start"], parms["finish"], parms["npts"]))

    if parms["feature"] in ("max", "min"):
        center = bec.peaks[parms["feature"]][signal.name][0]
    else:
        center = bec.peaks[parms["feature"]][signal.name]
    # fwhm = bec.peaks["fwhm"][signal.name]

    # confirm center will be within scan range
    assert min(parms["start"], parms["finish"]) <= round(center, 8)
    assert center <= max(parms["start"], parms["finish"])

    RE(bps.mv(mover, center))  # move to the center position
    position = get_position(mover)
    assert math.isclose(position, center, abs_tol=0.001)


@pytest.mark.iocs
@pytest.mark.skipif(
    in_gha_workflow(),
    reason="Deprecated code. Slow to run.  Don't bother testing in GHA.",
)
@pytest.mark.parametrize(
    "parms",
    [
        pytest.param(
            dict(signals=["noisy"], mover="m1", start=-1.2, finish=1.2, npts=11, feature="max", rescan=True),
            id="epics-noisy-max-rescan",
        ),
        pytest.param(
            dict(
                signals=["epics_pvoigt"], mover="axis", start=-1.2, finish=1.2, npts=11, feature="cen", rescan=True
            ),
            id="epics-pseudo-voigt-centroid-rescan",
        ),
        pytest.param(
            dict(
                signals=["epics_pvoigt"], mover="axis", start=-1.2, finish=1.2, npts=11, feature="max", rescan=True
            ),
            id="epics-pseudo-voigt-max-rescan",
        ),
        pytest.param(
            dict(
                signals=["epics_pvoigt"], mover="axis", start=-1.2, finish=1.2, npts=11, feature="max", rescan=True
            ),
            id="epics-pseudo-voigt-single-detector-rescan",
        ),
        pytest.param(
            dict(
                signals=["epics_pvoigt", "noisy", "scaler1"],
                mover="axis",
                start=-1.2,
                finish=1.2,
                npts=11,
                feature="max",
                rescan=True,
            ),
            id="epics-pseudo-voigt-noisy-scaler-detectors-rescan",
        ),
        pytest.param(
            dict(
                signals=["epics_pvoigt"], mover="axis", start=-1.2, finish=1.2, npts=11, feature="max", rescan=True
            ),
            id="epics-pseudo-voigt-tuple-detector-rescan",
        ),
        pytest.param(
            dict(
                signals=["epics_pvoigt"],
                mover="axis",
                start=-1.2,
                finish=1.2,
                npts=11,
                feature="cen",
                rescan=False,
            ),
            id="epics-pseudo-voigt-centroid-no-rescan",
        ),
        pytest.param(
            dict(
                signals=["epics_pvoigt"],
                mover="axis",
                start=-1.2,
                finish=1.2,
                npts=11,
                feature="com",
                rescan=False,
            ),
            id="epics-pseudo-voigt-center-of-mass-no-rescan",
        ),
        pytest.param(
            dict(
                signals=["epics_pvoigt"],
                mover="axis",
                start=-1.2,
                finish=1.2,
                npts=11,
                feature="max",
                rescan=False,
            ),
            id="epics-pseudo-voigt-max-no-rescan",
        ),
        pytest.param(
            dict(
                signals=["epics_pvoigt"],
                mover="axis",
                start=-1.2,
                finish=1.2,
                npts=11,
                feature="min",
                rescan=False,
            ),
            id="epics-pseudo-voigt-min-no-rescan",
        ),
    ],
)
def test_lineup(parms, RE: RunEngine, request: FixtureRequest, swait, m1):
    bec = RE.bec
    mover = request.getfixturevalue(parms["mover"])
    signals = [request.getfixturevalue(sig_name) for sig_name in parms["signals"]]
    if isinstance(signals[0], SynPseudoVoigt):
        signals[0].randomize_parameters(scale=250_000, bkg=0.000_000_000_1)
    else:
        change_noisy_parameters(swait, m1)

    RE(bps.mv(mover, 0))
    assert get_position(mover) == 0.0

    with pytest.deprecated_call():
        RE(
            alignment.lineup(
                signals,
                mover,
                parms["start"],
                parms["finish"],
                parms["npts"],
                feature=parms["feature"],
                rescan=parms["rescan"],
                bec=bec,
            )
        )

    # if parms["rescan"] and parms["feature"] in "max cen".split():
    #     # Test if mover position is within width of center.
    #     if isinstance(parms["signals"], SynPseudoVoigt):
    #         center = parms["signals"].center
    #         width = parms["signals"].sigma * 2.355  # FWHM approx.
    #     else:  # FIXME: multiple signals
    #         center = swait.channels.B.input_value.get()
    #         width = swait.channels.C.input_value.get()
    #     position = get_position(parms["mover"])
    #     lo = center-width
    #     hi = center+width
    #     # assert lo <= position <= hi, f"{bec=} {bec.peaks=} {position=} {center=} {width=}"


@pytest.mark.parametrize(
    "parms",
    [
        pytest.param(
            dict(
                signals=["simulated_pvoigt"],
                mover="simulated_mover",
                start=-1.2,
                finish=1.2,
                npts=11,
                feature="cen",
                nscans=2,
            ),
            id="pseudo-voigt-centroid-rescan",
        ),
        pytest.param(
            dict(
                signals=["simulated_pvoigt"],
                mover="simulated_mover",
                start=-1.2,
                finish=1.2,
                npts=11,
                feature="max",
                nscans=2,
            ),
            id="pseudo-voigt-max-rescan",
        ),
        pytest.param(
            dict(
                signals=["simulated_pvoigt"],
                mover="simulated_mover",
                start=-1.2,
                finish=1.2,
                npts=11,
                feature="max",
                nscans=2,
            ),
            id="pseudo-voigt-single-detector-rescan",
        ),
        pytest.param(
            dict(
                signals=["simulated_pvoigt"],
                mover="simulated_mover",
                start=-1.2,
                finish=1.2,
                npts=11,
                feature="max",
                nscans=2,
            ),
            id="pseudo-voigt-tuple-detector-rescan",
        ),
        pytest.param(
            dict(
                signals=["simulated_pvoigt"],
                mover="simulated_mover",
                start=-1.2,
                finish=1.2,
                npts=11,
                feature="cen",
                nscans=1,
            ),
            id="pseudo-voigt-centroid",
        ),
        pytest.param(
            dict(
                signals=["simulated_pvoigt"],
                mover="simulated_mover",
                start=-1.2,
                finish=1.2,
                npts=51,
                feature="com",
                nscans=1,
            ),
            id="pseudo-voigt-center-of-mass",
        ),
        pytest.param(
            dict(
                signals=["simulated_pvoigt"],
                mover="simulated_mover",
                start=-1.2,
                finish=1.2,
                npts=11,
                feature="max",
                nscans=1,
            ),
            id="pseudo-voigt-max",
        ),
        pytest.param(
            dict(
                signals=["simulated_pvoigt"],
                mover="simulated_mover",
                start=-1.2,
                finish=1.2,
                npts=11,
                feature="min",
                nscans=1,
            ),
            id="pseudo-voigt-min",
        ),
    ],
)
def test_lineup2(parms, RE: RunEngine, request, swait, m1):
    mover = request.getfixturevalue(parms["mover"])
    signals = [request.getfixturevalue(sig_name) for sig_name in parms["signals"]]
    if isinstance(signals[0], SynPseudoVoigt):
        signals[0].randomize_parameters(scale=250_000, bkg=0.000_000_000_1)
    else:
        change_noisy_parameters(swait, m1)

    RE(bps.mv(mover, 0))
    assert get_position(mover) == 0.0

    RE(
        alignment.lineup2(
            signals,
            mover,
            parms["start"],
            parms["finish"],
            parms["npts"],
            feature=parms["feature"],
            nscans=parms["nscans"],
        )
    )


@pytest.mark.iocs
@pytest.mark.parametrize("detector_names", [["noisy"], ["I0"], ["scaler1"], ["I0", "scaler1"]])
def test_lineup2_issue_1049(detector_names, RE: RunEngine, request: FixtureRequest, scaler1, I0, m1, tmp_path):
    detectors = [request.getfixturevalue(name) for name in detector_names]
    scaler1.select_channels(["I0"])
    assert len(scaler1.read_attrs) == 4, f"{scaler1.read_attrs=}"

    assert I0.name == "I0"
    assert I0.read().get("I0") is not None
    assert scaler1.read().get("I0") is not None

    uids = RE(alignment.lineup2(detectors, m1, -0.1, 0.1, 11, nscans=1))
    assert len(uids) == 1, f"{detectors=} {uids=}"

    specwriter = SpecWriterCallback2()
    specwriter.file_name = tmp_path / "alignment-1049.dat"
    uids = RE(
        alignment.lineup2(detectors, m1, -0.1, 0.1, 11, nscans=1),
        specwriter.receiver,
    )
    assert len(uids) == 1, f"{detectors=} {uids=}"


@pytest.mark.iocs
def test_TuneAxis(RE, m1, catalog):
    cat = catalog
    signal = SynPseudoVoigt(name="signal", motor=m1, motor_field=m1.name)
    signal.kind = "hinted"

    m1.tuner = alignment.TuneAxis([signal], m1)
    assert "tune" in dir(m1.tuner)

    npoints = 9
    with pytest.deprecated_call():
        uids = RE(m1.tuner.tune(width=4, num=npoints))
    assert len(uids) == 1

    stream_names = cat.v1[uids[-1]].stream_names
    assert ["PeakStats", "primary"] == sorted(stream_names)

    with pytest.deprecated_call():  # Databroker deprecation
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


@pytest.mark.iocs
def test_tune_axes(RE: RunEngine, m1, m2):
    signal = SynPseudoVoigt(name="signal", motor=m1, motor_field=m1.name)
    signal.kind = "hinted"

    axes = (m1, m2)
    for obj in axes:
        obj.tuner = alignment.TuneAxis([signal], obj)
        assert "tune" in dir(obj.tuner), f"{obj.name=}"

    uids = RE(alignment.tune_axes(axes))
    assert len(uids) == 2


@pytest.mark.iocs
def test_tune_axes_raises(RE: RunEngine, m1, m2):
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


def test_TuneResults(RE: RunEngine):
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


@pytest.mark.iocs
@pytest.mark.parametrize(
    "parms",
    [
        pytest.param(
            dict(
                peak=1e5,
                base=1e6,
                noise=10,
                center=0.1,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.05,
                outcome=False,
            ),
            id="signal-but-high-background",
        ),
        pytest.param(
            dict(
                peak=1e5,
                base=0,
                noise=10,
                center=0.1,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.06,
                outcome=True,
            ),
            id="model-peak",
        ),
        pytest.param(
            dict(
                peak=1e5,
                base=1e4,
                noise=10,
                center=0.1,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.1,
                outcome=True,
            ),
            id="high-background-poor-resolution",
        ),
        pytest.param(
            dict(
                peak=1e5,
                base=1e4,
                noise=10,
                center=0.1,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=2,
                tol=0.08,
                outcome=True,
            ),
            id="not-much-better",
        ),  # TODO: sigma
        pytest.param(
            dict(
                peak=-1e5,
                base=-1e4,
                noise=1e-8,
                center=0.1,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.1,
                outcome=True,
            ),
            id="negative-peak-one-times-base",
        ),
        pytest.param(
            dict(
                peak=1e5,
                base=-10,
                noise=10,
                center=0.1,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.06,
                outcome=True,
            ),
            id="negative-base",
        ),
        pytest.param(
            dict(
                peak=1e-5,
                base=0,
                noise=1e-8,
                center=0.1,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.06,
                outcome=True,
            ),
            id="small-signal-zero-base",
        ),
        pytest.param(
            dict(
                peak=-1e5,
                base=0,
                noise=1e-8,
                center=0.1,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.06,
                outcome=True,
            ),
            id="negative-small-signal-zero-base",
        ),  # TODO: sigma
        pytest.param(
            dict(
                peak=1e-5,
                base=1e-7,
                noise=1e-8,
                center=0.1,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.06,
                outcome=True,
            ),
            id="small-signal-finite-base",
        ),
        pytest.param(
            dict(
                peak=0,
                base=0,
                noise=1e-8,
                center=0.1,
                sigma=0.2,
                xlo=-1.0,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.05,
                outcome=False,
            ),
            id="no-signal-only-noise",
        ),
        pytest.param(
            dict(
                peak=0,
                base=1,
                noise=0.1,
                center=0.1,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.05,
                outcome=False,
            ),
            id="background-plus-noise",
        ),
        pytest.param(
            dict(
                peak=0,
                base=1,
                noise=100,
                center=10.0,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.05,
                outcome=False,
            ),
            id="background-plus-big-noise",
        ),
        pytest.param(
            dict(
                peak=0,
                base=0,
                noise=0,
                center=0.1,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.005,
                outcome=None,
            ),
            id="no-signal-zero-division-error",
        ),
        pytest.param(
            dict(
                peak=0,
                base=1,
                noise=0,
                center=0.1,
                sigma=0.2,
                xlo=-0.7,
                xhi=0.5,
                npts=11,
                nscans=1,
                tol=0.005,
                outcome=None,
            ),
            id="background-only-zero-division-error",
        ),
    ],
)
def test_lineup2_signal_permutations(parms, RE: RunEngine, m1, swait, noisy):
    starting_position = 0.0
    m1.move(starting_position)
    time.sleep(1)  # without this, the test IOC crashes, sometimes
    swait.reset()
    swait.description.put("CI test lineup2()")
    swait.channels.A.input_pv.put(m1.user_readback.pvname)
    swait.channels.B.input_value.put(parms["center"])
    swait.channels.C.input_value.put(parms["sigma"])
    swait.channels.D.input_value.put(parms["peak"])
    swait.channels.E.input_value.put(parms["base"])
    swait.channels.F.input_value.put(parms["noise"])
    swait.calculation.put("E+D/(1+((A-B)/C)^2)+F*RNDM")
    swait.scanning_rate.put("I/O Intr")

    stats = SignalStatsCallback()

    detector = noisy
    # fmt: off
    RE(
            alignment.lineup2(
                detector, m1, parms["xlo"], parms["xhi"], parms["npts"], nscans=parms["nscans"], signal_stats=stats
            )
        )
    # fmt: on
    change_noisy_parameters(swait, m1)

    try:
        centroid = stats.analysis.centroid
        if parms["outcome"]:
            assert math.isclose(m1.position, centroid, abs_tol=parms["tol"])
            assert math.isclose(parms["center"], centroid, abs_tol=parms["tol"])
        else:
            assert not math.isclose(parms["center"], centroid, abs_tol=parms["tol"])
    except ZeroDivisionError:
        assert math.isclose(m1.position, starting_position, abs_tol=parms["tol"])
