import time

import pytest

from ...tests import IOC
from ...tests import common_attribute_quantities_test
from ...tests import timed_pause
from ..calcout import CalcoutRecord
from ..calcout import UserCalcoutDevice
from ..calcout import setup_incrementer_calcout


@pytest.mark.parametrize(
    "device, pv, connect, attr, expected",
    [
        [CalcoutRecord, f"{IOC}userCalcOut10", False, "read_attrs", 12],
        [CalcoutRecord, f"{IOC}userCalcOut10", False, "configuration_attrs", 100],
        [CalcoutRecord, f"{IOC}userCalcOut10", True, "read()", 2],
        [CalcoutRecord, f"{IOC}userCalcOut10", True, "summary()", 220],

        [UserCalcoutDevice, IOC, False, "read_attrs", 130],
        [UserCalcoutDevice, IOC, False, "configuration_attrs", 1020],
        [UserCalcoutDevice, IOC, True, "read()", 20],
        [UserCalcoutDevice, IOC, True, "summary()", 2065],
    ]
)
def test_attribute_quantities(device, pv, connect, attr, expected):
    """Verify the quantities of the different attributes."""
    common_attribute_quantities_test(device, pv, connect, attr, expected)


def test_calcout_reset():
    user = UserCalcoutDevice(IOC, name="user")
    user.wait_for_connection()
    user.enable.put("Enable")

    calcout = user.calcout10
    assert isinstance(calcout, CalcoutRecord)
    calcout.enable.put("E")  # Note: only "E"

    setup_incrementer_calcout(calcout)
    time.sleep(0.2)
    assert calcout.description.get() == "incrementer"
    assert calcout.calculation.get() == "(A+1) % B"
    v1 = calcout.calculated_value.get()
    time.sleep(0.2)
    assert v1 < calcout.calculated_value.get()

    calcout.reset()
    timed_pause()
    assert calcout.description.get() == calcout.prefix
    assert calcout.calculation.get() == "0"
    v1 = calcout.calculated_value.get()
    time.sleep(0.2)
    assert v1 == calcout.calculated_value.get()
