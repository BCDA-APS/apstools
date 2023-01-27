import bluesky
import pytest
from ophyd import Component
from ophyd import Device
from ophyd import Signal

from .. import restorable_stage_sigs

RE = bluesky.RunEngine()


class MyTestDevice(Device):
    signal = Component(Signal, value=0.0)


@pytest.fixture(scope="function")
def device():
    yield MyTestDevice(name="device")


def rewrites_stage_sigs(obj):
    obj.stage_sigs = dict(signal=-1)
    yield from bluesky.plan_stubs.null()


def preserves_original_stage_sigs(obj):
    @restorable_stage_sigs([obj])
    def _inner():
        yield from rewrites_stage_sigs(obj)

    yield from _inner()


def test_device(device):
    assert hasattr(device, "signal")
    assert isinstance(device.signal, Signal)
    assert hasattr(device, "stage_sigs")
    assert isinstance(device.stage_sigs, dict)
    assert len(device.stage_sigs) == 0
    assert "signal" not in device.stage_sigs


@pytest.mark.parametrize(
    "plan, expected",
    # fmt: off
    [
        [rewrites_stage_sigs, 1],
        [preserves_original_stage_sigs, 0],
    ]
    # fmt: on
)
def test_plans(plan, expected, device):
    assert len(device.stage_sigs) == 0

    RE(plan(device))
    assert len(device.stage_sigs) == expected
