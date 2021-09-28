"""
test issue listplans() command
"""

from ..devices import SimulatedApsPssShutterWithStatus
from ..utils import listplans
import pandas as pd


def test_basic():
    result = listplans()
    assert result is not None
    assert isinstance(result, pd.DataFrame)
    assert len(result) == 0


def test_in_class():
    def f1():
        yield 1

    class C1:
        def f2(self):
            yield 1
    c1 = C1()

    result = listplans(c1)
    assert len(result) == 1


def test_shutter():
    shutter = SimulatedApsPssShutterWithStatus(name="shutter")
    result = listplans(shutter)
    assert len(result) == 5
    assert result["plan"][0] == "shutter.get_instantiated_signals"
    assert result["plan"][4] == "shutter.walk_subdevices"
