import pytest

from ...tests import IOC_GP
from ...tests import common_attribute_quantities_test
from ...tests import timed_pause
from ..swait import SwaitRecord
from ..swait import UserCalcN
from ..swait import UserCalcsDevice
from ..swait import setup_random_number_swait


@pytest.mark.parametrize(
    "device, pv, connect, attr, expected",
    [
        [SwaitRecord, f"{IOC_GP}userCalc10", False, "read_attrs", 12],
        [SwaitRecord, f"{IOC_GP}userCalc10", False, "configuration_attrs", 72],
        [SwaitRecord, f"{IOC_GP}userCalc10", True, "read()", 1],
        [SwaitRecord, f"{IOC_GP}userCalc10", True, "summary()", 162],
        [UserCalcN, f"{IOC_GP}userCalc10", False, "read_attrs", 12],
        [UserCalcN, f"{IOC_GP}userCalc10", False, "configuration_attrs", 73],
        [UserCalcN, f"{IOC_GP}userCalc10", True, "read()", 1],
        [UserCalcN, f"{IOC_GP}userCalc10", True, "summary()", 164],
        [UserCalcsDevice, IOC_GP, False, "read_attrs", 130],
        [UserCalcsDevice, IOC_GP, False, "configuration_attrs", 741],
        [UserCalcsDevice, IOC_GP, True, "read()", 10],
        [UserCalcsDevice, IOC_GP, True, "summary()", 1496],
    ],
)
def test_attribute_quantities(device, pv, connect, attr, expected):
    """Verify the quantities of the different attributes."""
    common_attribute_quantities_test(device, pv, connect, attr, expected)


def test_userCalcs_reset():
    user = UserCalcsDevice(IOC_GP, name="user")
    user.wait_for_connection()
    user.enable.put("Enable")

    swait = user.calc10
    assert isinstance(swait, SwaitRecord)
    swait.enable.put("E")  # Note: only "E"

    setup_random_number_swait(swait)
    timed_pause(0.2)
    assert swait.description.get() == "uniform random numbers"
    assert swait.calculation.get() == "RNDM"
    v1 = swait.calculated_value.get()
    timed_pause(0.2)
    assert v1 != swait.calculated_value.get()

    swait.reset()
    timed_pause()
    assert swait.description.get() == swait.prefix
    assert swait.calculation.get() == "0"
    v1 = swait.calculated_value.get()
    timed_pause(0.2)
    assert v1 == swait.calculated_value.get()
