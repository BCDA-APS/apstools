from .. import ContinuousScalerMotorFlyer
from .. import fly_scaler_motor
from ...tests import IOC
from bluesky import plans as bp
from bluesky import RunEngine
import databroker
import ophyd
import pytest
import time


cat = databroker.temp()
RE = RunEngine({})
RE.subscribe(cat.v1.insert)

m1 = ophyd.EpicsMotor(f"{IOC}m1", name="m1")
scaler1 = ophyd.scaler.ScalerCH(f"{IOC}scaler1", name="scaler1")
for obj in (m1, scaler1):
    obj.wait_for_connection()


@pytest.fixture(scope="function")
def flyer():
    obj = ContinuousScalerMotorFlyer(scaler1, m1, -1, 1, name="flyer")
    return obj


def test_kickoff(flyer):
    assert flyer is not None

    st = flyer.kickoff()
    assert not st.done
    assert isinstance(st, ophyd.DeviceStatus)

    time.sleep(0.000_001)
    assert st.done


def test_describe_collect(flyer):
    flyer.kickoff()
    schema = flyer.describe_collect()
    assert isinstance(schema, dict)


def test_collect(flyer):
    flyer.kickoff()
    event = flyer.collect()
    assert not isinstance(event, dict)

    events = list(event)
    assert isinstance(events, list)
    assert len(events) == 1
    assert "time" in events[0]
    assert "data" in events[0]
    assert "timestamps" in events[0]


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
    assert len(dataset.keys()) == 0  # wrote no data
