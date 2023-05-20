import time

import ophyd
import pytest

from ...tests import IOC_GP
from .. import make_dict_device

m1 = ophyd.EpicsMotor(f"{IOC_GP}m1", name="m1")
m1.wait_for_connection()


@pytest.mark.parametrize(
    "obj",
    [
        m1.read(),
        dict(a=1, b="two"),
        dict(a="a", b=dict(value="b", timestamp=time.time())),
        dict(a="a", b=dict(values="b", timestamp=time.time())),
        dict(a="a", b=dict(values="b")),
        dict(a="a", b=dict()),
        dict(a="a", b=dict(b=dict(b=dict(b=dict(b=dict()))))),
        dict(a="a", b=dict(value="b", timestamp=time.time(), temperature=25.2, units="any")),
    ],
)
def test_dict_device(obj):
    assert m1.connected

    m1_read = m1.read()
    ddev = make_dict_device(m1_read)
    for k in ddev.component_names:
        assert k in m1_read, k
    for k, v in ddev.read().items():
        k2 = k.lstrip(f"{ddev.name}_")
        assert k2 in m1_read
        assert v == m1_read[k2]
