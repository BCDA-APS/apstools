import time
from collections.abc import Mapping
from typing import Any

import ophyd
import pytest
from _pytest.fixtures import FixtureRequest, FixtureFunctionDefinition

from ...tests import IOC_GP
from .. import make_dict_device


@pytest.fixture(scope="module")
def m1():
    device_ = ophyd.EpicsMotor(f"{IOC_GP}m1", name="m1")
    device_.wait_for_connection()
    return device_


@pytest.mark.iocs
@pytest.mark.parametrize(
    "input_dict",
    [
        m1,
        dict(a=1, b="two"),
        dict(a="a", b=dict(value="b", timestamp=time.time())),
        dict(a="a", b=dict(values="b", timestamp=time.time())),
        dict(a="a", b=dict(values="b")),
        dict(a="a", b=dict()),
        dict(a="a", b=dict(b=dict(b=dict(b=dict(b=dict()))))),
        dict(a="a", b=dict(value="b", timestamp=time.time(), temperature=25.2, units="any")),
    ],
)
def test_dict_device(input_dict: Mapping[str, Any] | FixtureFunctionDefinition, request: FixtureRequest):
    if isinstance(input_dict, FixtureFunctionDefinition):
        # Allow both ophyd object fixtures and dictionaries as input
        device = request.getfixturevalue(input_dict.name)
        input_dict = device.read()

    ddev = make_dict_device(input_dict)
    for k in ddev.component_names:
        assert k in input_dict, k
    for k, v in ddev.read().items():
        k2 = k.removeprefix(f"{ddev.name}_")
        assert k2 in input_dict
        expected = input_dict[k2]
        if isinstance(expected, dict) and set(expected) == {"value", "timestamp"}:
            assert v == expected
        else:
            assert v["value"] == expected
