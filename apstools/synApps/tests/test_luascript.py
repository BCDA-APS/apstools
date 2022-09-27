import pytest

from ..luascript import LuascriptRecord
from ..luascript import UserScriptsDevice
from ...tests import common_attribute_quantities_test
from ...tests import IOC
from ...tests import short_delay_for_EPICS_IOC_database_processing


PV_PREFIX = f"{IOC}set1:"
EMPIRICAL_DELAY = 0.5

# TODO: test a luascript file, where to put the file in the IOC?
# LUA_SCRIPT_PATH
# https://epics-lua.readthedocs.io/en/latest/luascriptRecord.html?highlight=file#examples
# https://epics-lua.readthedocs.io/en/latest/using-lua-shell.html?highlight=file#calling-the-lua-shell-from-inside-the-ioc-shell


@pytest.mark.parametrize(
    "device, pv, connect, attr, expected",
    [
        [LuascriptRecord, f"{PV_PREFIX}userScript9", False, "read_attrs", 10],
        [LuascriptRecord, f"{PV_PREFIX}userScript9", False, "configuration_attrs", 98],
        [LuascriptRecord, f"{PV_PREFIX}userScript9", True, "read()", 2],
        [LuascriptRecord, f"{PV_PREFIX}userScript9", True, "summary()", 207],

        [UserScriptsDevice, PV_PREFIX, False, "read_attrs", 110],
        [UserScriptsDevice, PV_PREFIX, False, "configuration_attrs", 991],
        [UserScriptsDevice, PV_PREFIX, True, "read()", 20],
        [UserScriptsDevice, PV_PREFIX, True, "summary()", 1906],
    ]
)
def test_attribute_quantities(device, pv, connect, attr, expected):
    """Verify the quantities of the different attributes."""
    common_attribute_quantities_test(device, pv, connect, attr, expected)


def test_luascript_reset():
    lua_all = UserScriptsDevice(PV_PREFIX, name="user")
    lua_all.wait_for_connection()
    lua_all.enable.put("Enable")

    lua = lua_all.script9
    assert isinstance(lua, LuascriptRecord)

    lua_all.reset()
    lua.disable_value.put(2)  # ensure record is always enabled
    short_delay_for_EPICS_IOC_database_processing(EMPIRICAL_DELAY)  # a short-ish wait (discovered empirically)
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
    short_delay_for_EPICS_IOC_database_processing(EMPIRICAL_DELAY)  # a short-ish wait (discovered empirically)

    assert lua.precision.get() != 5
    assert lua.code.get() != ""
    assert lua.number_value.get() != 0
    assert lua.string_value.get() != ""
    assert lua.inputs.A.input_value.get() != 0
    assert lua.inputs.AA.pv_link.get() != ""
    assert lua.inputs.BB.input_value.get() != ""

    lua_all.reset()
    short_delay_for_EPICS_IOC_database_processing()

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
    short_delay_for_EPICS_IOC_database_processing()
    assert lua_all.enable.get(as_string=True) == "Enable"

    lua_all.reset()
    short_delay_for_EPICS_IOC_database_processing()

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
    short_delay_for_EPICS_IOC_database_processing(EMPIRICAL_DELAY)  # a short-ish wait (discovered empirically)

    assert round(lua.number_value.get(), 5) == nval
    assert lua.string_value.get() == sval

    lua_all.reset()
    short_delay_for_EPICS_IOC_database_processing()
