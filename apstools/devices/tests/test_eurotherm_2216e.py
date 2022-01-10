"""
test the Eurotherm 2216e device support

Hardware is not available so test with best efforts
"""

from .. import eurotherm_2216e

IOC = "gp:"
PV_PREFIX = f"phony:{IOC}2216e:"


def test_device():
    controller = eurotherm_2216e.Eurotherm2216e(
        PV_PREFIX, name="controller", readback_pv="rb", setpoint_pv="w"
    )
    assert not controller.connected
    assert controller.tolerance.get() == 1

    cns = """
    readback setpoint sensor
    done target tolerance report_dmov_changes
    mode power program_number
    """.split()
    assert sorted(controller.component_names) == sorted(cns)
