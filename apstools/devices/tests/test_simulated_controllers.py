"""
Test the simulated controllers.
"""

import math
import re
from contextlib import nullcontext as does_not_raise

import pytest
from ophyd.sim import instantiate_fake_device

from ...tests import IOC_GP
from ...tests import in_gha_workflow
from ...tests import timed_pause
from .. import simulated_controllers as sc

PV_SWAIT = f"{IOC_GP}userCalc7"
PV_TRANS = f"{IOC_GP}userTran7"


@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(controller_class=sc.SimulatedSwaitControllerPositioner),
            does_not_raise(),
            id="swait-structure",
        ),
        pytest.param(
            dict(controller_class=sc.SimulatedTransformControllerPositioner),
            does_not_raise(),
            id="transform-structure",
        ),
        pytest.param(
            dict(controller_class=sc.SimulatedSwaitControllerPositioner, loop_pv=""),
            pytest.raises(ValueError, match=re.escape("Must supply a value for 'loop_pv'.")),
            id="swait-requires-loop-pv",
        ),
        pytest.param(
            dict(controller_class=sc.SimulatedTransformControllerPositioner, loop_pv=" "),
            pytest.raises(ValueError, match=re.escape("Must supply a value for 'loop_pv'.")),
            id="transform-requires-loop-pv",
        ),
    ],
)
def test_fake_controller_structure(parms, context):
    with context:
        controller_class = parms["controller_class"]
        loop_pv = parms.get("loop_pv", "loop:")
        sim = instantiate_fake_device(controller_class, loop_pv=loop_pv, name="sim")
        assert sim.connected
        assert sim.readback.name == "sim"
        assert sim.setpoint.name == "sim_setpoint"
        assert sim.loop.name == "sim_loop"
        assert tuple(sim.component_names) == (
            "readback",
            "setpoint",
            "done",
            "tolerance",
            "report_dmov_changes",
            "target",
            "loop",
        )


@pytest.mark.skipif(
    in_gha_workflow(),
    reason="Random failures in GHA workflows.",
)
@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(sp=-55, pv=PV_SWAIT, controller_class=sc.SimulatedSwaitControllerPositioner, tol=0.99),
            does_not_raise(),
            id="swait-negative-setpoint",
        ),
        pytest.param(
            dict(sp=120, pv=PV_TRANS, controller_class=sc.SimulatedTransformControllerPositioner, tol=2),
            does_not_raise(),
            id="transform-positive-setpoint",
        ),
        pytest.param(
            dict(sp=998, pv=PV_SWAIT, controller_class=sc.SimulatedSwaitControllerPositioner, tol=5),
            does_not_raise(),
            id="swait-large-setpoint",
        ),
    ],
)
def test_live_controller_setup(parms, context):
    with context:
        sim = parms["controller_class"]("", loop_pv=parms["pv"], name="sim")
        sim.wait_for_connection()
        timed_pause()
        sim.setup(parms["sp"], tolerance=parms["tol"], noise=0.8 * parms["tol"])
        timed_pause()
        assert sim.connected
        assert math.isclose(sim.setpoint.get(), parms["sp"], abs_tol=0.01)
        assert math.isclose(sim.tolerance.get(), parms["tol"], abs_tol=0.0001)
        assert math.isclose(sim.position, parms["sp"], abs_tol=parms["tol"])
        assert sim.inposition
