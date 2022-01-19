import time

from apstools.synApps.tests.test_luascript import SHORT_DELAY_FOR_EPICS

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

    calc.reset()
    assert calc.enable.get() in [1, "E"]

    # set some things
    calc.description.put("unit testing")
    v = 1.23456
    calc.channels.A.input_value.put(v)
    calc.channels.BB.input_value.put("testing")
    calc.calculation.put("A")
    calc.process_record.put(1)
    time.sleep(SHORT_DELAY_FOR_EPICS)
    assert calc.channels.A.input_value.get() == v
    assert calc.channels.BB.input_value.get() == "testing"
    assert calc.calculation.get() == "A"
    assert round(calc.calculated_value.get(), 5) == v
    assert calc.calculated_value_string.get() == str(v)

    calc.reset()
    assert calc.description.get() == calc.prefix
    assert calc.calculation.get() == "0"
    assert calc.channels.A.input_value.get() == 0
    assert calc.channels.BB.input_value.get() == ""
    assert round(calc.calculated_value.get(), 5) == 0
    assert calc.calculated_value_string.get() == "0.00000"

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
