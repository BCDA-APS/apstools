import time

from ..swait import setup_random_number_swait
from ..swait import SwaitRecord
from ..swait import UserCalcsDevice


IOC = "gp:"


def test_read():
    swait = SwaitRecord(f"{IOC}userCalc10", name="sseq")
    assert swait is not None
    swait.wait_for_connection()

    assert len(swait.read_attrs) == 12
    assert len(swait.configuration_attrs) == 61
    assert len(swait._summary().splitlines()) == 152


def test_swait_reset():
    user = UserCalcsDevice(IOC, name="user")
    user.wait_for_connection()
    user.enable.put("Enable")
    assert len(user.read()) == 130

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
