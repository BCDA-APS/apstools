"""Test parts of the utils.misc module."""

import re
from contextlib import nullcontext as does_not_raise

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
    assert isinstance(result, str)
    assert result == expected, f"{original=!r}  {result=!r}  {expected=!r}"


@pytest.mark.parametrize(
    "parms, context",
    [
        pytest.param(
            dict(specified="ophyd.EpicsMotor", expected=ophyd.EpicsMotor),
            does_not_raise(),
            id="import ophyd.EpicsMotor",
        ),
        pytest.param(
            dict(specified="apstools.utils.dynamic_import", expected=dynamic_import),
            does_not_raise(),
            id="import apstools.utils.dynamic_import",
        ),
        pytest.param(
            dict(specified="apstools.utils.misc.cleanupText", expected=cleanupText),
            does_not_raise(),
            id="import apstools.utils.misc.cleanupText",
        ),
        pytest.param(
            dict(
                specified="apstools.utils._core.MAX_EPICS_STRINGOUT_LENGTH",
                expected=MAX_EPICS_STRINGOUT_LENGTH,
            ),
            does_not_raise(),
            id="import a module-level constant",
        ),
        pytest.param(
            dict(specified="CustomClass", expected=None),
            pytest.raises(ValueError, match=re.escape("Must use a dotted path, no local imports.")),
            id="unqualified name raises ValueError",
        ),
        pytest.param(
            dict(specified=".test_utils.CATALOG", expected=None),
            pytest.raises(ValueError, match=re.escape("Must use absolute path, no relative imports.")),
            id="relative import raises ValueError",
        ),
    ],
)
def test_dynamic_import(parms, context):
    with context:
        obj = dynamic_import(parms["specified"])
        assert obj == parms["expected"], f"{parms['specified']!r}  {obj=}  {parms['expected']=}"
