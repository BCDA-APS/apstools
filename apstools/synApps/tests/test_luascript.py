from ..luascript import LuascriptRecord
from ..luascript import UserScriptsDevice


IOC = "gp:"
PV_PREFIX = f"{IOC}set1:"


def test_read():
    lua = LuascriptRecord(f"{PV_PREFIX}userScript9", name="lua")
    assert lua is not None
    lua.wait_for_connection()

    assert len(lua.read_attrs) == 10
    assert len(lua.configuration_attrs) == 67
    assert len(lua._summary().splitlines()) == 175


# def test_swait_reset():
#     user = UserCalcsDevice(IOC, name="user")
#     user.wait_for_connection()
#     user.enable.put("Enable")
#     assert len(user.read()) == 130

#     swait = user.calc10
#     assert isinstance(swait, SwaitRecord)
#     swait.enable.put("E")  # Note: only "E"

#     setup_random_number_swait(swait)
#     time.sleep(0.2)
#     assert swait.description.get() == "uniform random numbers"
#     assert swait.calculation.get() == "RNDM"
#     v1 = swait.calculated_value.get()
#     time.sleep(0.2)
#     assert v1 != swait.calculated_value.get()

#     swait.reset()
#     assert swait.description.get() == swait.prefix
#     assert swait.calculation.get() == "0"
#     v1 = swait.calculated_value.get()
#     time.sleep(0.2)
#     assert v1 == swait.calculated_value.get()

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
