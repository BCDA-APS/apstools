import time

from ..scalcout import ScalcoutRecord
from ..scalcout import UserScalcoutDevice


IOC = "gp:"


def test_read():
    scalcout = ScalcoutRecord(f"{IOC}userStringCalc10", name="scalcout")
    assert scalcout is not None
    scalcout.wait_for_connection()

    assert len(scalcout.read_attrs) == 24
    assert len(scalcout.configuration_attrs) == 89
    assert len(scalcout._summary().splitlines()) == 227


def test_scalcout_reset():
    user = UserScalcoutDevice(IOC, name="user")
    user.wait_for_connection()
    user.enable.put("Enable")
    assert len(user.read()) == 280

    calc = user.scalcout10
    assert isinstance(calc, ScalcoutRecord)
    calc.enable.put("E")  # Note: only "E"

    # TODO: set some things

    calc.reset()
    assert calc.description.get() == calc.prefix
    assert calc.calculation.get() == "0"
    v1 = calc.calculated_value.get()
    time.sleep(0.2)
    assert v1 == calc.calculated_value.get()

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
