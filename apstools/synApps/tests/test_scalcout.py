import pytest

from ...tests import IOC_GP
from ...tests import common_attribute_quantities_test
from ...tests import timed_pause
from ..scalcout import ScalcoutRecord
from ..scalcout import UserScalcoutDevice


@pytest.mark.parametrize(
    "device, pv, connect, attr, expected",
    [
        [ScalcoutRecord, f"{IOC_GP}userStringCalc10", False, "read_attrs", 24],
        [ScalcoutRecord, f"{IOC_GP}userStringCalc10", False, "configuration_attrs", 114],
        [ScalcoutRecord, f"{IOC_GP}userStringCalc10", True, "read()", 3],
        [ScalcoutRecord, f"{IOC_GP}userStringCalc10", True, "summary()", 250],
        [UserScalcoutDevice, IOC_GP, False, "read_attrs", 250],
        [UserScalcoutDevice, IOC_GP, False, "configuration_attrs", 1160],
        [UserScalcoutDevice, IOC_GP, True, "read()", 30],
        [UserScalcoutDevice, IOC_GP, True, "summary()", 2355],
    ],
)
def test_attribute_quantities(device, pv, connect, attr, expected):
    """Verify the quantities of the different attributes."""
    common_attribute_quantities_test(device, pv, connect, attr, expected)


def test_scalcout_reset():
    user = UserScalcoutDevice(IOC_GP, name="user")
    user.wait_for_connection()
    user.enable.put("Enable")

    calc = user.scalcout10
    assert isinstance(calc, ScalcoutRecord)

    calc.reset()
    timed_pause()
    assert calc.enable.get() in [1, "E"]

    # set some things
    calc.description.put("unit testing")
    v = 1.23456
    calc.channels.A.input_value.put(v)
    calc.channels.BB.input_value.put("testing")
    calc.calculation.put("A")
    calc.process_record.put(1)
    timed_pause()
    assert calc.channels.A.input_value.get() == v
    assert calc.channels.BB.input_value.get() == "testing"
    assert calc.calculation.get() == "A"
    assert round(calc.calculated_value.get(), 5) == v
    assert calc.calculated_value_string.get() == str(v)

    calc.reset()
    timed_pause()
    assert calc.description.get() == calc.prefix
    assert calc.calculation.get() == "0"
    assert calc.channels.A.input_value.get() == 0
    assert calc.channels.BB.input_value.get() == ""
    assert round(calc.calculated_value.get(), 5) == 0
    assert calc.calculated_value_string.get() == "0.00000"

    v1 = calc.calculated_value.get()
    timed_pause(0.2)
    assert v1 == calc.calculated_value.get()
