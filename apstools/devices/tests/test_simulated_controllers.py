"""
Test the simulated controllers.
"""

import math
from contextlib import nullcontext as does_not_raise

import pytest

from ...tests import IOC_GP
from ...tests import timed_pause
from .. import simulated_controllers as sc

PV_SWAIT = f"{IOC_GP}userCalc7"
PV_TRANS = f"{IOC_GP}userTran7"


@pytest.mark.parametrize("sp", [-55, 120, 998])
@pytest.mark.parametrize(
    "pv, controller_class, context, exp_info",
    [
        [PV_SWAIT, sc.SimulatedSwaitControllerPositioner, does_not_raise(), "None"],
        [PV_TRANS, sc.SimulatedTransformControllerPositioner, does_not_raise(), "None"],
        ["", sc.SimulatedSwaitControllerPositioner, pytest.raises(ValueError), "Must supply a value for"],
        ["", sc.SimulatedTransformControllerPositioner, pytest.raises(ValueError), "Must supply a value for"],
        ["wrong_pv", sc.SimulatedSwaitControllerPositioner, pytest.raises(TimeoutError), "Failed to connect"],
        ["wrong_pv", sc.SimulatedTransformControllerPositioner, pytest.raises(TimeoutError), "Failed to connect"],
    ],
)
@pytest.mark.parametrize("tol", [0.99, 2, 5])
def test_simulators(sp, pv, controller_class, context, exp_info, tol):
    """
    Test the simulator.
    """
    with context as info:
        sim = controller_class("", loop_pv=pv, name="sim")
        sim.wait_for_connection()
    assert exp_info in str(info), f"{str(info)=!r}"
    if exp_info != "None":
        return

    timed_pause()
    assert sim.connected

    sim.setup(sp, tolerance=tol, noise=0.8 * tol)
    timed_pause()

    assert math.isclose(sim.setpoint.get(), sp, abs_tol=0.01)
    assert math.isclose(sim.tolerance.get(), tol, abs_tol=0.0001)
    assert math.isclose(sim.position, sp, abs_tol=tol)
    assert sim.inposition
