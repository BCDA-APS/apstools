import pytest
import time

from ..luascript import LuascriptRecord
from ..luascript import UserScriptsDevice
from ...__init__ import SHORT_DELAY_FOR_EPICS_IOC_DATABASE_PROCESSING


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

    lua = lua_all.script9
    assert isinstance(lua, LuascriptRecord)

    lua_all.reset()
    lua.disable_value.put(2)  # ensure record is always enabled
    time.sleep(EMPIRICAL_DELAY)  # a short-ish wait (discovered empirically)
    assert (
        lua.scan_disable_input_link_value.get() != lua.disable_value.get()
    )

    assert lua.precision.get() == 5
    assert lua.code.get() == ""
    assert lua.number_value.get() == 0
    assert lua.string_value.get() == ""
    assert lua.inputs.A.input_value.get() == 0
    assert lua.inputs.AA.pv_link.get() == ""
    assert lua.inputs.BB.input_value.get() == ""

    lua.precision.put(3)
    lua.number_value.put(-3.7)
    lua.string_value.put("string_value")
    lua.inputs.A.input_value.put(-2)
    lua.inputs.AA.pv_link.put("string_pv_link")
    lua.inputs.BB.input_value.put("BB.input_value")
    # order is important, set this LAST
    lua.code.put("code")
    time.sleep(EMPIRICAL_DELAY)  # a short-ish wait (discovered empirically)

    assert lua.precision.get() != 5
    assert lua.code.get() != ""
    assert lua.number_value.get() != 0
    assert lua.string_value.get() != ""
    assert lua.inputs.A.input_value.get() != 0
    assert lua.inputs.AA.pv_link.get() != ""
    assert lua.inputs.BB.input_value.get() != ""

    lua_all.reset()

    assert lua.precision.get() == 5
    assert lua.code.get() == ""
    assert lua.number_value.get() == 0
    assert lua.string_value.get() == ""
    assert lua.inputs.A.input_value.get() == 0
    assert lua.inputs.AA.pv_link.get() == ""
    assert lua.inputs.BB.input_value.get() == ""


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
    time.sleep(SHORT_DELAY_FOR_EPICS_IOC_DATABASE_PROCESSING)
    assert lua_all.enable.get(as_string=True) == "Enable"

    lua_all.reset()

    lua = lua_all.script9
    lua.disable_value.put(2)  # ensure record is always enabled
    assert (
        lua.scan_disable_input_link_value.get() != lua.disable_value.get()
    )

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
