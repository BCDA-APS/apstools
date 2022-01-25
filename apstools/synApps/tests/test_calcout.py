import time

from ..calcout import setup_incrementer_calcout
from ..calcout import CalcoutRecord
from ..calcout import UserCalcoutDevice
from ...tests import IOC


def test_read():
    calcout = CalcoutRecord(f"{IOC}userCalcOut10", name="sseq")
    assert calcout is not None
    calcout.wait_for_connection()

    assert len(calcout.read_attrs) == 12
    assert len(calcout.configuration_attrs) == 52
    assert len(calcout._summary().splitlines()) == 172


def test_calcout_reset():
    user = UserCalcoutDevice(IOC, name="user")
    user.wait_for_connection()
    user.enable.put("Enable")
    assert len(user.read()) == 500

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
    assert calcout.description.get() == calcout.prefix
    assert calcout.calculation.get() == "0"
    v1 = calcout.calculated_value.get()
    time.sleep(0.2)
    assert v1 == calcout.calculated_value.get()

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
