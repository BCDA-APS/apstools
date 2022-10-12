from .. import ContinuousScalerMotorFlyer
from .. import fly_scaler_motor
from ...tests import IOC
from bluesky import plans as bp
from bluesky import RunEngine
import databroker
import ophyd
import pytest
import time


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
STREAM_NAME = "primary"
START = -1
FINISH = 1
VELOCITY = 2


@pytest.fixture(scope="function")
def flyer():
    obj = ContinuousScalerMotorFlyer(
        scaler1, m1, START, FINISH, velocity=VELOCITY, name="flyer"
    )
    return obj


def test_kickoff(flyer):
    assert flyer is not None

    very_short_time = 0.000_1

    kickoff_status = flyer.kickoff()
    assert isinstance(kickoff_status, ophyd.DeviceStatus)
    if flyer.mode.get() == "kickoff":
        assert flyer._readings == []
    kickoff_status.wait()
    assert kickoff_status.done

    while flyer.mode.get() == "kickoff":  # check next mode
        time.sleep(very_short_time)
    assert flyer.mode.get() in ("taxi", "fly", "return", "idle")

    assert not flyer.flyscan_complete_status.done
    assert flyer.mode.get() in flyer._action_modes
    while flyer.mode.get() == "taxi":  # check next mode
        time.sleep(very_short_time)
    assert flyer.mode.get() in ("fly", "return", "idle")

    assert flyer._old_scaler_reading is not None
    assert kickoff_status.done
    assert not flyer.flyscan_complete_status.done

    while flyer.mode.get() == "fly":  # check next mode
        time.sleep(very_short_time)
    assert flyer.mode.get() in ("return", "idle")

    while flyer.mode.get() == "return":  # check next mode
        time.sleep(very_short_time)
    assert flyer.mode.get() == "idle"

    flyer.flyscan_complete_status.wait()
    assert flyer.flyscan_complete_status.done


def test_describe_collect(flyer):
    flyer.kickoff()
    schema = flyer.describe_collect()
    assert isinstance(schema, dict)
    assert STREAM_NAME in schema
    for key in READING_KEY_LIST:
        assert key in schema[STREAM_NAME]


def test_collect(flyer):
    flyer.kickoff()
    assert isinstance(flyer.flyscan_complete_status, ophyd.DeviceStatus)
    while flyer.mode.get() in ("idle", "kickoff"):
        time.sleep(0.000_1)
    assert flyer.mode.get() == "taxi"

    # while flyer.mode.get() in ("taxi"):
    #     time.sleep(0.000_1)

    flyer.flyscan_complete_status.wait()
    assert len(flyer._readings) > 0

    event = flyer.collect()
    readings = flyer._readings.copy()
    assert len(readings) > 0
    assert not isinstance(event, dict)

    events = list(event)
    assert isinstance(events, list)
    assert len(events) == len(readings)
    for event in events:
        assert "time" in event
        assert "data" in event
        assert "timestamps" in event
        assert isinstance(event["time"], (int, float))
        for key in READING_KEY_LIST:
            assert key in event["data"]
            assert key in event["timestamps"]


@pytest.mark.parametrize("method", ["device", "plan"])
def test_flyer(method, flyer):
    if method == "device":
        uids = RE(bp.fly([flyer]))
    elif method == "plan":
        uids = RE(fly_scaler_motor(scaler1, m1, -1, 1))
    else:
        raise ValueError(f"Unknown {method=}.")
    assert len(uids) == 1

    run = cat.v2[uids[-1]]
    assert run is not None
    assert hasattr(run, "primary")

    dataset = run.primary.read()
    assert dataset is not None
    assert len(dataset.keys()) == len(READING_KEY_LIST)
