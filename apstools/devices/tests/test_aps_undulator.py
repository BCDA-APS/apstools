import pytest
from ophyd.sim import instantiate_fake_device

from ..aps_undulator import PlanarUndulator


@pytest.fixture()
def undulator():
    undulator = instantiate_fake_device(PlanarUndulator, prefix="PSS:255ID:", name="undulator")
    return undulator


def test_set_energy(undulator):
    assert undulator.start_button.get() == 0
    undulator.energy.set(5)
    assert undulator.energy.setpoint.get() == 5
    assert undulator.start_button.get() == 1


def test_stop_energy(undulator):
    assert undulator.stop_button.get() == 0
    undulator.stop()
    assert undulator.stop_button.get() == 1
