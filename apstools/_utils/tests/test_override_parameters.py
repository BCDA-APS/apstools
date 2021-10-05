"""
test override_parameters module
"""

from apstools.utils import OverrideParameters
import numpy as np
import pandas as pd
import pytest


@pytest.fixture(scope="function")
def overrides():
    return OverrideParameters()


def test_initial(overrides):
    assert overrides is not None
    assert len(overrides._parameters) == 0


def test_missing(overrides):
    parm = "no such parameter"
    assert parm not in overrides._parameters
    assert overrides.pick(parm, "test value") == "test value"


def test_register(overrides):
    parm = "test_parameter"
    assert parm not in overrides._parameters
    assert len(overrides._parameters) == 0

    overrides.register(parm)
    assert parm in overrides._parameters
    assert len(overrides._parameters) == 1

    overrides.register(parm)
    assert len(overrides._parameters) == 1


def test_undefined(overrides):
    parm = "test_parameter"
    overrides.register(parm)
    assert overrides._parameters[parm] == overrides.undefined
    assert overrides.pick(parm, overrides.undefined) == overrides.undefined
    assert overrides.pick(parm, "undefined") != overrides.undefined
    assert overrides.pick(parm, "undefined") == "undefined"

    overrides.set(parm, 1)
    assert overrides.pick(parm, "undefined") != overrides.undefined
    assert overrides.pick(parm, "undefined") == 1


def test_reset(overrides):
    parm = "test_parameter"
    overrides.register(parm)
    assert overrides.pick(parm, "undefined") == "undefined"

    overrides.set(parm, 1)
    assert overrides.pick(parm, "undefined") == 1

    overrides.reset(parm)
    assert overrides.pick(parm, "undefined") == "undefined"


def test_reset_all(overrides):
    parm = "test_parameter"
    overrides.register(parm)
    assert overrides.pick(parm, "undefined") == "undefined"

    overrides.set(parm, 1)
    assert overrides.pick(parm, "undefined") == 1

    overrides.reset_all()
    assert overrides.pick(parm, "undefined") == "undefined"


def test_summary_type(overrides):
    assert isinstance(overrides.summary(), pd.DataFrame)


def test_summary(overrides):
    parm = "test_parameter"
    assert len(overrides.summary()) == 0

    overrides.register(parm)
    summary = overrides.summary()
    assert len(summary) != 0

    assert summary.columns[0] == "parameter"
    assert summary.columns[1] == "value"

    expected = np.array([[parm, overrides.undefined]])
    assert not (expected == summary.values).all()

    expected = np.array([[parm, "--undefined--"]])
    assert (expected == summary.values).all()
