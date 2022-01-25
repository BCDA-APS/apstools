import pytest
import time

from ..swait import setup_random_number_swait
from ..swait import SwaitRecord
from ..swait import UserCalcN
from ..swait import UserCalcsDevice
from ...tests import common_attribute_quantities_test
from ...tests import IOC
# from ...tests import SHORT_DELAY_FOR_EPICS_IOC_DATABASE_PROCESSING


@pytest.mark.parametrize(
    "device, pv, connect, attr, expected",
    [
        [SwaitRecord, f"{IOC}userCalc10", False, "read_attrs", 12],
        [SwaitRecord, f"{IOC}userCalc10", False, "configuration_attrs", 72],
        [SwaitRecord, f"{IOC}userCalc10", True, "read()", 1],
        [SwaitRecord, f"{IOC}userCalc10", True, "summary()", 162],

        [UserCalcN, f"{IOC}userCalc10", False, "read_attrs", 12],
        [UserCalcN, f"{IOC}userCalc10", False, "configuration_attrs", 73],
        [UserCalcN, f"{IOC}userCalc10", True, "read()", 1],
        [UserCalcN, f"{IOC}userCalc10", True, "summary()", 164],

        [UserCalcsDevice, IOC, False, "read_attrs", 130],
        [UserCalcsDevice, IOC, False, "configuration_attrs", 741],
        [UserCalcsDevice, IOC, True, "read()", 10],
        [UserCalcsDevice, IOC, True, "summary()", 1496],
    ]
)
def test_attribute_quantities(device, pv, connect, attr, expected):
    """Verify the quantities of the different attributes."""
    common_attribute_quantities_test(device, pv, connect, attr, expected)


def test_userCalcs_reset():
    user = UserCalcsDevice(IOC, name="user")
    user.wait_for_connection()
    user.enable.put("Enable")

    swait = user.calc10
    assert isinstance(swait, SwaitRecord)
    swait.enable.put("E")  # Note: only "E"

    setup_random_number_swait(swait)
    time.sleep(0.2)
    assert swait.description.get() == "uniform random numbers"
    assert swait.calculation.get() == "RNDM"
    v1 = swait.calculated_value.get()
    time.sleep(0.2)
    assert v1 != swait.calculated_value.get()

    swait.reset()
    assert swait.description.get() == swait.prefix
    assert swait.calculation.get() == "0"
    v1 = swait.calculated_value.get()
    time.sleep(0.2)
    assert v1 == swait.calculated_value.get()

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
