"""
test the Eurotherm 2216e device support

Hardware is not available so test with best efforts
"""

from ..lakeshore_controllers import LakeShore336Device, LakeShore340Device

IOC = "gp:"
PV_PREFIX = f"phony:{IOC}lakeshore:"


def test_lakeshore_336():
    t336 = LakeShore336Device(PV_PREFIX, name="lakeshore336")
    assert not t336.connected

    # Signal components
    assert t336.loop1.target.get() == "None"
    assert t336.loop2.target.get() == "None"

    assert t336.loop1.tolerance.get() == 0.1
    assert t336.loop2.tolerance.get() == 0.1

    assert t336.loop1.settle_time == 0
    assert t336.loop2.settle_time == 0

    # Read attrs
    cns = """
    loop1 loop1.readback loop1.setpoint loop1.heater loop2 loop2.readback
    loop2.setpoint loop2.heater loop3 loop3.readback loop4 loop4.readback
    """.split()
    assert sorted(t336.read_attrs) == sorted(cns)

    # Components
    cns = """
    loop1 loop2 loop3 loop4 scanning_rate process_record read_all serial
    """.split()
    assert sorted(t336.component_names) == sorted(cns)

    cns = """
    readback setpoint done tolerance report_dmov_changes target units heater
    heater_range pid_P pid_I pid_D ramp_rate ramp_on loop_name control manual
    mode
    """.split()
    assert sorted(t336.loop1.component_names) == sorted(cns)

    cns = """
    readback setpoint done tolerance report_dmov_changes target units heater
    heater_range pid_P pid_I pid_D ramp_rate ramp_on loop_name control manual
    mode
    """.split()
    assert sorted(t336.loop2.component_names) == sorted(cns)

    cns = """
    readback units loop_name
    """.split()
    assert sorted(t336.loop3.component_names) == sorted(cns)

    cns = """
    readback units loop_name
    """.split()
    assert sorted(t336.loop3.component_names) == sorted(cns)


def test_lakeshore_340():
    t340 = LakeShore340Device(PV_PREFIX, name="lakeshore340")
    assert not t340.connected

    # Signal components
    assert t340.control.target.get() == "None"
    assert t340.sample.target.get() == "None"

    assert t340.control.tolerance.get() == 0.1
    assert t340.sample.tolerance.get() == 0.1

    assert t340.control.settle_time == 0
    assert t340.sample.settle_time == 0

    # Read attrs
    cns = """
    control control.readback control.setpoint sample sample.readback
    sample.setpoint heater heater_range
    """.split()
    assert sorted(t340.read_attrs) == sorted(cns)

    # Components
    cns = """
    control sample heater heater_range read_pid scanning_rate process_record
    serial
    """.split()
    assert sorted(t340.component_names) == sorted(cns)

    cns = """
    readback setpoint done tolerance report_dmov_changes target units pid_P
    pid_I pid_D ramp_rate ramp_on sensor
    """.split()
    assert sorted(t340.control.component_names) == sorted(cns)

    cns = """
    readback setpoint done tolerance report_dmov_changes target units pid_P
    pid_I pid_D ramp_rate ramp_on sensor
    """.split()
    assert sorted(t340.sample.component_names) == sorted(cns)
