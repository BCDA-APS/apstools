"""
Test execution of a blocking function in a plan.
"""

import random
import time

import bluesky
import pytest
from ophyd import EpicsSignal

from ...tests import IOC_GP
from .. import run_blocking_function

PV = f"{IOC_GP}gp:float1"
T_MIN = 0.1
T_RANDOM_SCALE = 0.3
T_MAX = T_MIN + T_RANDOM_SCALE * random.random() + 1


def create_signal():
    signal = EpicsSignal(PV, name="signal")
    signal.wait_for_connection()
    return signal


def procedure(signal, target_value):
    signal_now = signal.get(use_monitor=False)
    if signal_now == target_value:
        target_value += signal_now

    signal.put(target_value, use_complete=True)

    # finite, random delay, <= T_MAX
    time.sleep(T_MIN + T_RANDOM_SCALE * random.random())
    return target_value


@pytest.mark.parametrize(
    # fmt:off
    "target, expected, random_start",
    [
        [.1, .1, True],
        [.1, .2, False],
        [.2, .4, False],
        [.3, .3, False],
        [.1, .1, False],
    ]
    # fmt:on
)
def test_direct(target, expected, random_start):
    signal = create_signal()
    assert isinstance(signal, EpicsSignal)
    if random_start:
        signal.put(random.random())

    # test direct use, as from command-line, new target
    t0 = time.time()
    response = procedure(signal, target)
    dt = time.time() - t0
    assert T_MIN <= dt <= T_MAX
    assert response == expected
    assert signal.get() == expected


@pytest.mark.parametrize(
    # fmt:off
    "target, expected, random_start",
    [
        [.1, .1, True],
        [.1, .2, False],
        [.2, .4, False],
        [.3, .3, False],
        [.1, .1, False],
    ]
    # fmt:on
)
def test_bluesky(target, expected, random_start):
    signal = create_signal()
    assert isinstance(signal, EpicsSignal)
    if random_start:
        signal.put(random.random())

    RE = bluesky.RunEngine({})

    # test from RunEngine, different (original) target
    t0 = time.time()
    RE(run_blocking_function(procedure, signal, target))
    dt = time.time() - t0
    assert T_MIN <= dt <= T_MAX, f"{T_MIN=:.3f} {dt=:.3f} {T_MAX=:.3f}"
    assert signal.get() == expected
