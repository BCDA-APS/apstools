"""Test the alignment plans."""

# TODO: TuneAxis
# TODO: tune_axes
# TODO: TuneResults

from .. import alignment
from ... import utils
from ...devices import SynPseudoVoigt
from ...synApps import setup_lorentzian_swait
from ...synApps import SwaitRecord
from ...tests import IOC
from bluesky import RunEngine
from bluesky.callbacks import best_effort
import bluesky.plans as bp
import bluesky.plan_stubs as bps
import databroker
import numpy
import ophyd
import pytest

bec = best_effort.BestEffortCallback()
cat = databroker.temp()
RE = RunEngine({})
RE.subscribe(cat.v1.insert)
RE.subscribe(bec)
bec.enable_plots()
# utils.ipython_shell_namespace()["bec"] = bec
# globals()["bec"] = bec

axis = ophyd.EpicsSignal(f"{IOC}gp:float1", name="axis")
m1 = ophyd.EpicsMotor(f"{IOC}m1", name="m1")
noisy = ophyd.EpicsSignalRO(f"{IOC}userCalc1.VAL", name="noisy")
scaler1 = ophyd.scaler.ScalerCH(f"{IOC}scaler1", name="scaler1")
swait = SwaitRecord(f"{IOC}userCalc1", name="swait")

for obj in (axis, m1, noisy, scaler1, swait):
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
        position = obj.position
    else:
        position = obj.get()
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
        # FIXME: [noisy, m1, -1.2, 1.2, 11, "max"],  # slower
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
    # FIXME: else:
    #     change_noisy_parameters()

    RE(bp.rel_scan([signal], mover, start, finish, npts))
    analysis = bec.peaks[feature][signal.name]
    if isinstance(analysis, tuple):
        analysis = analysis[0]
    RE(bps.mv(mover, analysis))
    assert get_position(mover) == round(analysis, 3)

    if feature in "max cen".split():
        # Test if ended close to the expected value.
        if isinstance(signal, SynPseudoVoigt):
            center = signal.center
            width = signal.sigma * 2.355  # FWHM approx.
        # FIXME: else:
        #     center = swait.channels.B.input_value.get()
        #     width = swait.channels.C.input_value.get()
        position = get_position(mover)
        lo = center-width
        hi = center+width
        fwhm = bec.peaks["fwhm"][signal.name]
        assert lo <= position+fwhm, f"{lo=} {position=} {fwhm=}"
        assert position-fwhm < hi, f"{position=} {fwhm=} {hi=}"


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
