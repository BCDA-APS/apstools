"""
Test the Excel support.
"""

import pathlib

import pytest

from ...plans import command_list
from ...utils import ExcelDatabaseFileGeneric

DATA_PATH = pathlib.Path(command_list.__file__).parent / "tests"


@pytest.fixture(scope="function")
def xl_file():
    xl_file = DATA_PATH / "demo3.xlsx"
    return xl_file


def test_testfile_exists(xl_file):
    assert DATA_PATH.exists()
    assert xl_file.exists()


def test_normal_read(xl_file):
    xl = ExcelDatabaseFileGeneric(xl_file)
    assert len(xl.db) == 9  # rows
    assert len(xl.db["0"]) == 7  # columns
    assert "Unnamed: 7" in xl.db["0"]
    assert xl.db["0"]["Unnamed: 7"] == 8.0


def test_ignore_extra_false(xl_file):
    xl = ExcelDatabaseFileGeneric(xl_file, ignore_extra=False)
    assert len(xl.db) == 16  # rows
    assert len(xl.db["0"]) == 9  # columns
