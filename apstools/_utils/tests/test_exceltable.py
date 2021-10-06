"""
Test the Excel support.
"""

import os
import pytest

from ...utils import ExcelDatabaseFileGeneric


DATA_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "tests")
)


@pytest.fixture(scope="function")
def xl_file():
    xl_file = os.path.join(DATA_PATH, "demo3.xlsx")
    return xl_file


def test_testfile_exists(xl_file):
    assert os.path.exists(xl_file)


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
