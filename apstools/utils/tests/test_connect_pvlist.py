from ..misc import connect_pvlist
import pytest


@pytest.mark.parametrize(
    "pvlist, success",
    [
        ["ad:cam1:Acquire gp:UPTIME".split(), True],
    ]
)
def test_connect_pvlist(pvlist, success):
    assert isinstance(pvlist, list)
    pvdict = connect_pvlist(pvlist)
    assert isinstance(pvdict, dict)
