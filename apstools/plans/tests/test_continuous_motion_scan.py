from .. import ContinuousScalerMotorFlyer
from .. import fly_scaler_motor
from bluesky import plans as bp
from bluesky import RunEngine
import databroker
import pytest
from ophyd import DeviceStatus
import time


cat = databroker.temp()
RE = RunEngine({})
RE.subscribe(cat.v1.insert)


def test_kickoff():
    flyer = ContinuousScalerMotorFlyer(name="flyer")
    assert flyer is not None

    st = flyer.kickoff()
    assert not st.done
    assert isinstance(st, DeviceStatus)

    time.sleep(0.000_001)
    assert st.done


def test_describe_collect():
    flyer = ContinuousScalerMotorFlyer(name="flyer")
    flyer.kickoff()
    schema = flyer.describe_collect()
    assert isinstance(schema, dict)


def test_collect():
    flyer = ContinuousScalerMotorFlyer(name="flyer")
    flyer.kickoff()
    event = flyer.collect()
    assert not isinstance(event, dict)

    events = list(event)
    assert isinstance(events, list)
    assert len(events) == 1
    assert "time" in events[0]
    assert "data" in events[0]
    assert "timestamps" in events[0]


@pytest.mark.parametrize(
    "method", ["device", "plan"]
)
def test_flyer(method):
    if method == "device":
        flyer = ContinuousScalerMotorFlyer(name="flyer")
        uids = RE(bp.fly([flyer]))
    elif method == "plan":
        uids = RE(fly_scaler_motor())
    else:
        raise ValueError(f"Unknown {method=}.")
    assert len(uids) == 1

    run = cat.v2[uids[-1]]
    assert run is not None
    assert hasattr(run, "primary")

    dataset = run.primary.read()
    assert dataset is not None
    assert len(dataset.keys()) == 0  # wrote no data
