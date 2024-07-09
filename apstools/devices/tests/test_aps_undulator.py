import pytest
from ophyd.sim import instantiate_fake_device

from ..aps_undulator import PlanarUndulator
from ..aps_undulator import Revolver_Undulator
from ..aps_undulator import STI_Undulator
from ..aps_undulator import Undulator2M


@pytest.mark.parametrize(
    "klass, prefix",
    [
        [PlanarUndulator, "PSS:255ID:"],
        [Undulator2M, "PSS:255ID:"],
        [Revolver_Undulator, "PSS:255ID:"],
        [STI_Undulator, "PSS:255ID:"],
    ],
)
def test_set_energy(klass, prefix):
    undulator = instantiate_fake_device(klass, prefix=prefix, name="undulator")

    assert undulator.start_button.get() == 0
    undulator.energy.set(5)
    assert undulator.energy.setpoint.get() == 5
    assert undulator.start_button.get() == 1


@pytest.mark.parametrize(
    "klass, prefix",
    [
        [PlanarUndulator, "PSS:255ID:"],
        [Undulator2M, "S01ID:DSID:"],
        [Revolver_Undulator, "S08ID:USID:"],
        [STI_Undulator, "S04ID:USID:"],
    ],
)
def test_stop_energy(klass, prefix):
    undulator = instantiate_fake_device(klass, prefix=prefix, name="undulator")

    assert undulator.stop_button.get() == 0
    undulator.stop()
    assert undulator.stop_button.get() == 1
