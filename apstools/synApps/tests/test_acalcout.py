"""Test the aCalcout support."""

import math
import time

import pytest

from ...tests import IOC_GP
from ...tests import common_attribute_quantities_test
from ...tests import timed_pause
from .. import AcalcoutRecord
from .. import UserArrayCalcDevice

TEST_PV = f"{IOC_GP}userArrayCalc10"


def test_connected():
    acalcout = AcalcoutRecord(TEST_PV, name="acalcout")
    timed_pause(0.25)
    if not acalcout.connected:
        for nm in acalcout.component_names:
            assert getattr(acalcout, nm).connected, f"{nm}"


@pytest.mark.parametrize(
    "device, pv, connect, attr, expected",
    [
        [AcalcoutRecord, TEST_PV, False, "read_attrs", 12],
        [AcalcoutRecord, TEST_PV, False, "configuration_attrs", 127],
        [AcalcoutRecord, TEST_PV, True, "read()", 4],
        [AcalcoutRecord, TEST_PV, True, "summary()", 266],
        [UserArrayCalcDevice, IOC_GP, False, "read_attrs", 130],
        [UserArrayCalcDevice, IOC_GP, False, "configuration_attrs", 1290],
        [UserArrayCalcDevice, IOC_GP, True, "read()", 40],
        [UserArrayCalcDevice, IOC_GP, True, "summary()", 2505],
    ],
)
def test_attribute_quantities(device, pv, connect, attr, expected):
    """Verify the quantities of the different attributes."""
    common_attribute_quantities_test(device, pv, connect, attr, expected)


def test_calcout_reset():
    user = UserArrayCalcDevice(IOC_GP, name="user")
    user.wait_for_connection(timeout=10)
    user.enable.put("Enable")

    acalcout = user.acalcout10
    assert isinstance(acalcout, AcalcoutRecord)
    acalcout.enable.put("E")  # Note: only "E"

    # Change a few things from the default so reset can be tested.
    timed_pause()
    acalcout.description.put("sum the AA array")
    acalcout.channels.AA.input_value.put([0, 0, 5, 0, 0])
    acalcout.array_elements_used.put(5)
    acalcout.calculation.put("sum(AA)")
    timed_pause()
    assert math.isclose(5, acalcout.calculated_value.get(), abs_tol=0.1)

    # Reset and test for defaults.
    acalcout.reset()
    timed_pause()
    assert acalcout.description.get() == acalcout.prefix
    assert acalcout.calculation.get() == "0"
    assert acalcout.array_elements_used.get() == acalcout.array_elements_allocated.get()
    v1 = acalcout.calculated_value.get()
    time.sleep(0.2)
    assert v1 == acalcout.calculated_value.get()
