"""Test parts of the utils.misc module."""

import ophyd
import pytest

from .._core import MAX_EPICS_STRINGOUT_LENGTH
from ..misc import cleanupText
from ..misc import dynamic_import


class CustomClass:
    """some local class"""


@pytest.mark.parametrize(
    "original, expected, replacement",
    [
        ["abcd12345", "abcd12345", None],
        ["aBcd12345", "aBcd12345", None],
        ["abcd 12345", "abcd_12345", None],
        ["abcd-12345", "abcd_12345", None],
        ["  abc  ", "__abc__", None],
        ["  abc  ", "__abc__", None],
        ["  abc  ", "__abc__", "_"],
        ["  abc  ", "..abc..", "."],
    ],
)
def test_cleaupText(original, expected, replacement):
    result = cleanupText(original, replace=replacement)
    assert result == expected, f"{original=!r}  {result=!r}  {expected=!r}"


@pytest.mark.parametrize(
    "specified, expected, error",
    [
        ["ophyd.EpicsMotor", ophyd.EpicsMotor, None],
        ["apstools.utils.dynamic_import", dynamic_import, None],
        ["apstools.utils.misc.cleanupText", cleanupText, None],
        [
            "apstools.utils._core.MAX_EPICS_STRINGOUT_LENGTH",
            MAX_EPICS_STRINGOUT_LENGTH,
            None,
        ],
        ["CustomClass", None, ValueError],
        [".test_utils.CATALOG", None, ValueError],
    ],
)
def test_dynamic_import(specified, expected, error):
    if error is None:
        obj = dynamic_import(specified)
        assert obj == expected, f"{specified=!r}  {obj=}  {expected=}"
    else:
        with pytest.raises(error):
            obj = dynamic_import(specified)
