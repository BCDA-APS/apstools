import pytest
import time

from ..luascript import LuascriptRecord
from ..luascript import UserScriptsDevice


IOC = "gp:"
PV_PREFIX = f"{IOC}set1:"
EMPIRICAL_DELAY = 0.5

# TODO: test a luascript file, where to put the file in the IOC?
# LUA_SCRIPT_PATH
# https://epics-lua.readthedocs.io/en/latest/luascriptRecord.html?highlight=file#examples
# https://epics-lua.readthedocs.io/en/latest/using-lua-shell.html?highlight=file#calling-the-lua-shell-from-inside-the-ioc-shell


def test_read():
    lua = LuascriptRecord(f"{PV_PREFIX}userScript9", name="lua")
    assert lua is not None
    # lua.wait_for_connection()

    assert len(lua.read_attrs) == 10
    assert len(lua.configuration_attrs) == 78
    assert len(lua._summary().splitlines()) == 187


def test_luascript_reset():
    lua_all = UserScriptsDevice(PV_PREFIX, name="user")
    lua_all.wait_for_connection()
    lua_all.enable.put("Enable")
    assert len(lua_all.read()) == 220

    luarec = lua_all.script9
    assert isinstance(luarec, LuascriptRecord)

    lua_all.reset()
    assert lua_all.enable.get(as_string=True) == "Enable"

    assert luarec.precision.get() == 5
    assert luarec.code.get() == ""
    assert luarec.number_value.get() == 0
    assert luarec.string_value.get() == ""
    assert luarec.inputs.A.input_value.get() == 0
    assert luarec.inputs.AA.pv_link.get() == ""
    assert luarec.inputs.BB.input_value.get() == ""

    luarec.precision.put(3)
    luarec.number_value.put(-3.7)
    luarec.string_value.put("string_value")
    luarec.inputs.A.input_value.put(-2)
    luarec.inputs.AA.pv_link.put("string_pv_link")
    luarec.inputs.BB.input_value.put("BB.input_value")
    # order is important, set this LAST
    luarec.code.put("code")
    time.sleep(EMPIRICAL_DELAY)  # a short-ish wait (discovered empirically)

    assert luarec.precision.get() != 5
    assert luarec.code.get() != ""
    assert luarec.number_value.get() != 0
    assert luarec.string_value.get() != ""
    assert luarec.inputs.A.input_value.get() != 0
    assert luarec.inputs.AA.pv_link.get() != ""
    assert luarec.inputs.BB.input_value.get() != ""

    lua_all.reset()

    assert luarec.precision.get() == 5
    assert luarec.code.get() == ""
    assert luarec.number_value.get() == 0
    assert luarec.string_value.get() == ""
    assert luarec.inputs.A.input_value.get() == 0
    assert luarec.inputs.AA.pv_link.get() == ""
    assert luarec.inputs.BB.input_value.get() == ""


@pytest.mark.parametrize(
    "code, a, b, nval, aa, bb, sval",
    [
        ['return "A"', 0, 0, 0, "", "", "A"],
        ["return A+B", 5, -3, 2, "", "", ""],
        ["return A+B  --this is a comment", 5, -3, 2, "", "", ""],
        ['return string.rep(".", 5)', 0, 0, 0, "", "", "....."],
        ['return string.len("parametrize")', 0, 0, 11, "", "", ""],
        ['return "AA" .. "BB"', 0, 0, 0, "", "", "AABB"],

        # TODO: string variables are not recognized in luascript 3.0.1 in the test VM.
        # Wait for the test VM to be upgraded to at least 3.0.2 before enabling these tests.
        # FIXME: ["return string.upper(AA)", 0, 0, 0, "Abc", "", "ABC"],
        # FIXME: ["return string.lower(AA)", 0, 0, 0, "Abc", "", "abc"],
        # FIXME: ["return AA .. BB", 0, 0, 0, "Aaa", "Bbb", "AaaBbb"],
    ]
)
def test_compute(code, a, b, nval, aa, bb, sval):
    lua_all = UserScriptsDevice(PV_PREFIX, name="user")
    lua_all.wait_for_connection()
    lua_all.enable.put("Enable")
    assert lua_all.enable.get(as_string=True) == "Enable"

    lua_all.reset()
    assert lua_all.enable.get(as_string=True) == "Enable"

    lua = lua_all.script9

    # set the inputs
    lua.inputs.A.input_value.put(a)
    lua.inputs.B.input_value.put(b)
    lua.inputs.AA.input_value.put(aa)
    lua.inputs.BB.input_value.put(bb)

    # set the lua code
    lua.code.put(code)

    # not computed yet
    assert round(lua.number_value.get(), 5) == 0
    assert lua.string_value.get() == ""

    # do the computation
    assert lua_all.enable.get(as_string=True) == "Enable"
    assert lua.scan_disable_input_link_value.get() == lua_all.enable.get(as_string=False)
    lua.process_record.put(1)
    time.sleep(EMPIRICAL_DELAY)  # a short-ish wait (discovered empirically)

    assert round(lua.number_value.get(), 5) == nval
    assert lua.string_value.get() == sval

    lua.reset()

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
