import pytest
from ophyd.sim import instantiate_fake_device

from ..aps_undulator import PlanarUndulator
from ..aps_undulator import Revolver_Undulator
from ..aps_undulator import STI_Undulator
from ..aps_undulator import Undulator2M
from ..aps_undulator import Undulator4M


TEST_PV_PREFIX = "TEST:PREFIX:"
TEST_CASES = [
    [PlanarUndulator, TEST_PV_PREFIX],
    [Revolver_Undulator, TEST_PV_PREFIX],
    [STI_Undulator, TEST_PV_PREFIX],
    [Undulator2M, TEST_PV_PREFIX],
    [Undulator4M, TEST_PV_PREFIX],
]


@pytest.mark.parametrize("klass, prefix", TEST_CASES)
def test_set_energy(klass, prefix):
    undulator = instantiate_fake_device(klass, prefix=prefix, name="undulator")

    assert undulator.start_button.get() == 0
    undulator.energy.set(5)
    assert undulator.energy.setpoint.get() == 5
    assert undulator.start_button.get() == 1


@pytest.mark.parametrize("klass, prefix", TEST_CASES)
def test_stop_energy(klass, prefix):
    undulator = instantiate_fake_device(klass, prefix=prefix, name="undulator")

    assert undulator.stop_button.get() == 0
    undulator.stop()
    assert undulator.stop_button.get() == 1
