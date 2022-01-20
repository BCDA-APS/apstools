"""
test the Eurotherm 2216e device support

Hardware is not available so test with best efforts
"""

from .. import eurotherm_2216e
from ...tests import IOC

PV_PREFIX = f"phony:{IOC}2216e:"


def test_device():
    euro = eurotherm_2216e.Eurotherm2216e(PV_PREFIX, name="controller")
    assert not euro.connected

    assert euro.tolerance.get() == 1
    assert euro.update_target is False
    assert euro.target is None

    cns = """
    readback setpoint
    """.split()
    assert sorted(euro.read_attrs) == sorted(cns)

    cns += """
    sensor
    done tolerance report_dmov_changes
    mode power program_number
    """.split()
    assert sorted(euro.component_names) == sorted(cns)
