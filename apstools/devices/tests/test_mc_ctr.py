"""
test the Measurement Computing USB-CTR device support

Hardware is not available so test the Python (ophyd) structure.
"""

from ...tests import IOC_GP
from .. import measComp_usb_ctr_support

PV_PREFIX = f"phony:{IOC_GP}ctr:"


def test_MeasCompCtr():
    controller = measComp_usb_ctr_support.MeasCompCtr(PV_PREFIX, name="controller")
    assert not controller.connected

    for attr in """
        model_name
        model_number
        firmware_version
        unique_id
        ul_version
        driver_version
        poll_time_ms
        poll_sleep_ms
        last_error_message
    """.split():
        assert attr in controller.configuration_attrs, f"{attr}"

    attrs = """
    long_in long_out
    """.split()
    for i in range(4):
        attrs.append(f"pulse_gen_{i+1}")
        for a in "count delay duty_cycle frequency idle_state period run width".split():
            attrs.append(f"pulse_gen_{i+1}.{a}")
    for i in range(8):
        attrs.append(f"binary_in_{i+1}")
        attrs.append(f"binary_out_{i+1}")
        attrs.append(f"binary_direction_{i+1}")
        attrs.append(f"counter_{i+1}")
        attrs.append(f"counter_{i+1}.counts")
    for attr in attrs:
        assert attr in controller.read_attrs, f"{attr}"
    assert len(attrs) == len(controller.read_attrs)


def test_MeasCompCtrMcs():
    controller = measComp_usb_ctr_support.MeasCompCtrMcs(PV_PREFIX, name="controller")
    assert not controller.connected

    # spot-check some of the config attributes
    for attr in """
        acquiring
        dwell
        max_channels
        model
        prescale
        prescale_counter
        trigger_mode
    """.split():
        assert attr in controller.configuration_attrs, f"{attr}"

    attrs = [f"mca{i+1}" for i in range(8)]
    attrs.append("absolute_timebase_waveform")
    attrs.append("elapsed_real")
    for attr in attrs:
        assert attr in controller.read_attrs, f"{attr}"
    assert len(attrs) == len(controller.read_attrs)
