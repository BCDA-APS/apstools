import databroker
import pytest
from bluesky import RunEngine
from ophyd import EpicsMotor

from ...synApps import UserCalcN
from ...synApps import setup_random_number_swait
from ...tests import IOC_GP
from ...utils import getDefaultNamespace
from ..nscan_support import nscan

WAIT_TIMEOUT = 10


@pytest.fixture(scope="function")
def m1():
    obj = EpicsMotor(f"{IOC_GP}m1", name="m1", labels=["motor", "positioner"])
    obj.wait_for_connection(timeout=WAIT_TIMEOUT)

    ns = getDefaultNamespace()
    ns[obj.name] = obj
    yield obj

    ns.pop(obj.name)


@pytest.fixture(scope="function")
def m2():
    obj = EpicsMotor(f"{IOC_GP}m2", name="m2", labels=["motor", "positioner"])
    obj.wait_for_connection(timeout=WAIT_TIMEOUT)

    ns = getDefaultNamespace()
    ns[obj.name] = obj
    yield obj

    ns.pop(obj.name)


@pytest.fixture(scope="function")
def noisy():
    obj = UserCalcN(f"{IOC_GP}userCalc1", name="noisy", labels=["detector"])
    obj.wait_for_connection(timeout=WAIT_TIMEOUT)

    obj.calculated_value.name = obj.name

    ns = getDefaultNamespace()
    ns[obj.name] = obj

    # Configure the *detector* as a random number
    # generator using a calculation.
    setup_random_number_swait(obj)

    yield obj

    ns.pop(obj.name)


@pytest.mark.parametrize(
    "exc, dets, motor_sets, message",
    [
        [TypeError, [], [], "nscan() missing 1 required positional argument: 'detectors'"],
        [ValueError, [], [None], "must provide at least one movable"],
        [ValueError, [None], [None], "must provide at least one movable"],
        [ValueError, [None], [None] * 4, "must provide sets of movable, start, finish"],
        [ValueError, [None], [None] * 3, "start=None (<class 'NoneType'>): is not a number"],
        [ValueError, [None], [None] * 6, "start=None (<class 'NoneType'>): is not a number"],
    ],
)
def test_raises(exc, dets, motor_sets, message):
    RE = RunEngine()
    args = dets + motor_sets
    with pytest.raises(exc) as exinfo:
        RE(nscan(*args))
    assert message in str(exinfo.value)


def test_pl_nscan(m1, m2, noisy):
    cat = databroker.temp().v2
    RE = RunEngine()
    RE.subscribe(cat.v1.insert)

    npoints = 6
    uids = RE(nscan([noisy], m1, 0.2, 0, m2, -0.4, 0, num=npoints))
    assert len(uids) == 1

    run = cat[uids[0]]
    assert run is not None

    md_start = run.metadata["start"]
    assert len(md_start) > 0

    expected_keys = """
        detectors motors
        num_points num_intervals
        plan_args plan_name plan_pattern
        hints
    """.split()
    for k in expected_keys:
        assert k in md_start, f"{k=}"
    assert md_start.get("plan_name") == "nscan"
    assert md_start["num_points"] == md_start["num_intervals"] + 1
    assert md_start["num_points"] == npoints

    assert "primary" in dir(run)
    ds = run.primary.read()
    for k in (m1, m2, noisy):
        assert k.name in ds, f"{k=} {list(ds.keys())=}"
        assert len(ds[k.name]) == npoints, f"{k=}"
