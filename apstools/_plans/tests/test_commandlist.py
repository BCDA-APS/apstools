"""
Test the command list support.
"""

import os
import pyRestTable
import pytest

from ...plans import CommandFileReadError
from ...plans import get_command_list
from ...utils import command_list_as_table

DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "tests")
)


@pytest.fixture(scope="function")
def text_command_file():
    text_command_file = os.path.join(DATA_PATH, "actions.txt")
    return text_command_file


@pytest.fixture(scope="function")
def xl_command_file():
    xl_command_file = os.path.join(DATA_PATH, "actions.xlsx")
    return xl_command_file


@pytest.fixture(scope="function")
def xl_file():
    xl_file = os.path.join(DATA_PATH, "demo3.xlsx")
    return xl_file


def test_testfile_exists(text_command_file, xl_command_file, xl_file):
    assert os.path.exists(text_command_file)
    assert os.path.exists(xl_command_file)
    assert os.path.exists(xl_file)


def compare_tables_as_str(expected, received):
    e_lines = expected.strip().splitlines()
    r_lines = received.strip().splitlines()
    assert len(e_lines) == len(r_lines)
    for expect, got in zip(e_lines, r_lines):
        assert expect.strip() == got.strip()


def test_ExcelFile_commands(xl_file):
    # just a spreadsheet for testing (early version of a command file)
    commands = get_command_list(xl_file)
    assert len(commands) == 9  # rows

    table = command_list_as_table(commands, show_raw=False)
    assert isinstance(table, pyRestTable.Table)
    received = str(table).strip()
    expected = """
    ====== ====== =========================================
    line # action parameters
    ====== ====== =========================================
    1      row1   91, 26, 85, None, blank, 8
    2      row2   9, 39, 29, 85, sample, 60
    3      row3   54, None, 38, 3, blank, 76
    4      row4   71, 36, 95, 83, foil, 12
    5      row5   55, 75, 59, 84, DNA, 34
    6      row6   18, 49, 31, 34, lecithin, 47
    7      row7   37, None, None, None, a big mix  of stuff
    8      row8   37, 80, 79, 45, salt water, 36
    9      row9   72, 98, 67, 89, surprises, 49
    ====== ====== =========================================
    """.strip()
    compare_tables_as_str(expected, received)


def test_ExcelCommandList(xl_command_file):
    commands = get_command_list(xl_command_file)
    assert len(commands) == 7
    table = command_list_as_table(commands, show_raw=False)
    received = str(table).strip()
    expected = """
    ====== ============ ===========================
    line # action       parameters
    ====== ============ ===========================
    1      mono_shutter open
    2      USAXSscan    45.07, 98.3, 0, Water Blank
    3      saxsExp      45.07, 98.3, 0, Water Blank
    4      waxwsExp     45.07, 98.3, 0, Water Blank
    5      USAXSscan    12, 12, 1.2, plastic
    6      USAXSscan    12, 37, 0.1, Al foil
    7      mono_shutter close
    ====== ============ ===========================
    """.strip()
    compare_tables_as_str(expected, received)


def test_TextCommandList(text_command_file):
    commands = get_command_list(text_command_file)
    assert len(commands) == 5
    table = command_list_as_table(commands, show_raw=False)
    received = str(table).strip()
    expected = """
    ====== ============ ========================
    line # action       parameters
    ====== ============ ========================
    5      sample_slits 0, 0, 0.4, 1.2
    7      preusaxstune
    10     FlyScan      0, 0, 0, blank
    11     FlyScan      5, 2, 0, empty container
    12     SAXS         0, 0, 0, blank
    ====== ============ ========================
    """.strip()
    compare_tables_as_str(expected, received)


def test_TextCommandListRaw(text_command_file):
    commands = get_command_list(text_command_file)
    assert len(commands) == 5
    table = command_list_as_table(commands, show_raw=True)
    received = str(table).strip()
    expected = """
    ====== ============ ======================== =====================================
    line # action       parameters               raw input
    ====== ============ ======================== =====================================
    5      sample_slits 0, 0, 0.4, 1.2           sample_slits 0 0 0.4 1.2
    7      preusaxstune                          preusaxstune
    10     FlyScan      0, 0, 0, blank           FlyScan 0   0   0   blank
    11     FlyScan      5, 2, 0, empty container FlyScan 5   2   0   "empty container"
    12     SAXS         0, 0, 0, blank           SAXS 0 0 0 blank
    ====== ============ ======================== =====================================
    """.strip()
    compare_tables_as_str(expected, received)


@pytest.mark.parametrize(
    "error, expected, item",
    [
        (IOError, "file not found: ", os.path.join(DATA_PATH, "none such")),
        (CommandFileReadError, "could not read ", __file__),
    ],
)
def test_known_exceptions(error, expected, item):
    with pytest.raises(error) as exc:
        get_command_list(item)
    assert str(exc.value).startswith(expected)
