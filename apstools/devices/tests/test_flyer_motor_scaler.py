# FIXME: refactor for new code

from .. import ActionsFlyerBase
from .. import FlyerBase
from .. import ScalerMotorFlyer
from .. import SignalValueStack
from ...tests import IOC
from bluesky import plans as bp
from bluesky import RunEngine
import databroker
import ophyd
import pysumreg
import pytest
import time
import uuid


cat = databroker.temp().v2
RE = RunEngine({})
RE.subscribe(cat.v1.insert)

m1 = ophyd.EpicsMotor(f"{IOC}m1", name="m1")
scaler1 = ophyd.scaler.ScalerCH(f"{IOC}scaler1", name="scaler1")
for obj in (m1, scaler1):
    obj.wait_for_connection()
scaler1.select_channels()

READING_KEY_LIST = []
for obj in (m1, scaler1):
    READING_KEY_LIST += list(obj.read().keys())
NUM_READING_KEYS = len(READING_KEY_LIST)
STREAM_NAME = "primary"
START = -1
FINISH = 1


def test_SignalValueStack():
    original = m1.motor_egu.get()
    new_text = str(uuid.uuid4())[:10]
    assert original != new_text

    stack = SignalValueStack()
    stack.remember(m1.motor_egu)
    assert m1.motor_egu.get() == original

    m1.motor_egu.put(new_text)
    assert m1.motor_egu.get(use_monitor=False) != original
    assert m1.motor_egu.get() == new_text

    stack.restore()
    assert m1.motor_egu.get(use_monitor=False) == original
    assert m1.motor_egu.get() != new_text


@pytest.mark.parametrize("flyer_class", [FlyerBase, ActionsFlyerBase])
def test_bases(flyer_class):
    flyer = flyer_class(name="flyer")
    assert isinstance(flyer, flyer_class)
    assert not hasattr(flyer, "action_exception")

    uids = RE(bp.fly([flyer]))
    assert len(uids) == 1

    run = cat.v2[uids[-1]]
    assert run is not None
    assert hasattr(run, "primary")

    dataset = run.primary.read()
    assert dataset is not None
    assert len(dataset.keys()) == 0

    assert not hasattr(flyer, "stats")


@pytest.mark.parametrize(
    "start, finish, fly_time, fly_time_pad, period, n_keys, n_data",
    [
        [-1, 1, None, None, None, NUM_READING_KEYS, 10],
        [-1, 1, 2, 2, 1, NUM_READING_KEYS, 2],
        [-1, 1, 1, 2, 0.1, NUM_READING_KEYS, 10],
        [0, 0, 1, 2, 0.1, NUM_READING_KEYS, 0],
        [1, -1, 1, 2, 0.1, NUM_READING_KEYS, 10],
    ],
)
def test_ScalerMotorFlyer(start, finish, fly_time, fly_time_pad, period, n_keys, n_data):
    flyer = ScalerMotorFlyer(
        scaler1, m1, start, finish, name="flyer", fly_time=fly_time, fly_time_pad=fly_time_pad, period=period
    )
    assert isinstance(flyer, ScalerMotorFlyer)
    assert hasattr(flyer, "action_exception")

    uids = RE(bp.fly([flyer]))
    assert flyer.action_exception is None
    assert len(uids) == 1

    run = cat.v2[uids[-1]]
    assert run is not None
    assert hasattr(run, "primary")

    dataset = run.primary.read()
    assert dataset is not None
    assert len(dataset.keys()) == n_keys

    key = READING_KEY_LIST[0]
    assert key in dataset

    array = dataset[key].values
    assert n_data <= len(array) <= n_data + 3

    # spot check some statistics
    assert hasattr(flyer, "stats")
    assert isinstance(flyer.stats, dict)

    skeys = list(flyer.stats.keys())
    assert len(skeys) < NUM_READING_KEYS
    for k in skeys:
        assert k in READING_KEY_LIST, k

    ch = f"{scaler1.time.name}"
    assert ch in flyer.stats

    ch_stats = flyer.stats[ch]
    assert isinstance(ch_stats, pysumreg.SummationRegisters)
    assert ch_stats.n == len(array)

    lo = min(start, finish)
    hi = max(start, finish)
    if ch_stats.n == 0:
        assert ch_stats.min_x is None
        assert ch_stats.max_x is None
        # avoid ZeroDivisionErrors
        stats_dict = ch_stats.to_dict()
        assert stats_dict["mean_x"] is None
        assert stats_dict["centroid"] is None
    else:
        assert ch_stats.min_x >= lo
        assert ch_stats.max_x <= hi
        assert lo <= ch_stats.mean_x <= hi
        assert lo <= ch_stats.centroid <= hi


@pytest.mark.parametrize(
    "scaler, motor, fly_time, fly_time_pad, period, ex_class, text",
    [
        [scaler1, m1, -1, None, None, ValueError, "POSITIVE number"],
        [scaler1, m1, "number", None, None, TypeError, ""],
        [scaler1, m1, 1, -1, None, ValueError, "POSITIVE number"],
        [scaler1, m1, 1, 1, -1, ValueError, "POSITIVE number"],
        [scaler1, scaler1, 1, 1, 1, TypeError, "Unprepared to handle as motor"],
        [m1, m1, 1, 1, 1, TypeError, "Unprepared to handle as scaler"],
    ],
)
def test_ScalerMotorFlyerExceptions(scaler, motor, fly_time, fly_time_pad, period, ex_class, text):
    with pytest.raises(ex_class) as exc:
        ScalerMotorFlyer(
            scaler, motor, -1, 1, name="flyer", fly_time=fly_time, fly_time_pad=fly_time_pad, period=period
        )
    assert text in str(exc.value)


@pytest.mark.parametrize(
    "period, ex_class, text",
    [
        [0.01, ValueError, "Could not get requested scaler sample period"],
    ],
)
def test_period_exception(period, ex_class, text):
    flyer = ScalerMotorFlyer(scaler1, m1, -1, 1, name="flyer", period=period)

    RE(bp.fly([flyer]))
    assert len(flyer._readings) == 0
    assert flyer.action_exception is not None
    assert isinstance(flyer.action_exception, ex_class)
    assert text in str(flyer.action_exception)
