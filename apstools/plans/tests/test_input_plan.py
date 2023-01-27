import databroker
import pytest
from bluesky import RunEngine

from ..input_plan import request_input

cat = databroker.temp()
RE = RunEngine({})
RE.subscribe(cat.v1.insert)


def my_plan(msg, default, agree, bypass):
    yield from request_input(
        msg=msg,
        default=default,
        agree=agree,
        bypass=bypass,
    )


@pytest.mark.parametrize(
    "msg, default, agree, bypass",
    [
        # TODO: re-enable pending bluesky/bluesky#1550
        # ["Continue?", "y", "y", False],
        ["Continue?", "y", "y", True],
        [None, None, None, True],
        ["Continue?", "n", "y", True],
        ["Continue?", "n", ["y", "Sure", "certainly"], True],
        ["Continue?", "n", "n", True],
    ],
)
def test(msg, default, agree, bypass):
    if bypass:
        uids = RE(my_plan(msg, default, agree, bypass))
        assert isinstance(uids, (list, tuple))
    else:
        with pytest.raises(ValueError) as exinfo:
            RE(my_plan(msg, default, agree, bypass))
        assert str(exinfo.value).startswith("Invalid file object")
