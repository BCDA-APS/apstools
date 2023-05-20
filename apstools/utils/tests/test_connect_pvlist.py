import pytest

from ..misc import connect_pvlist
from ...tests import IOC_AD
from ...tests import IOC


@pytest.mark.parametrize(
    "pvlist, success",
    [
        [f"{IOC_AD}cam1:Acquire {IOC}UPTIME".split(), True],
    ],
)
def test_connect_pvlist(pvlist, success):
    assert isinstance(pvlist, list)
    pvdict = connect_pvlist(pvlist)
    assert isinstance(pvdict, dict)
