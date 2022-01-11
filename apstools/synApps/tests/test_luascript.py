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


def test_luascript_reset():
    lua_all = UserScriptsDevice(PV_PREFIX, name="user")
    lua_all.wait_for_connection()
    lua_all.enable.put("Enable")
    assert len(lua_all.read()) == 220

    luarec = lua_all.script0
    assert isinstance(luarec, LuascriptRecord)

    luarec.precision.put(3)
    luarec.code.put("code")
    luarec.number_value.put(-3.7)
    luarec.string_value.put("string_value")
    luarec.channels.A.number_input_value.put(-2)
    luarec.channels.A.string_input_pv.put("string_input_pv")

    assert luarec.precision.get() != 5
    assert luarec.code.get() != ""
    assert luarec.number_value.get() != 0
    assert luarec.string_value.get() != ""
    assert luarec.channels.A.number_input_value.get() != 0
    assert luarec.channels.A.string_input_pv.get() != ""

    luarec.reset()

    assert luarec.precision.get() == 5
    assert luarec.code.get() == ""
    assert luarec.number_value.get() == 0
    assert luarec.string_value.get() == ""
    assert luarec.channels.A.number_input_value.get() == 0
    assert luarec.channels.A.string_input_pv.get() == ""

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
