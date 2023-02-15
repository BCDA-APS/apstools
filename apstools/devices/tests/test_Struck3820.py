import pytest

from ..struck3820 import Struck3820

COMPONENT_NAMES = """
    start_all
    stop_all
    erase_start
    erase_all
    mca1
    mca2
    mca3
    mca4
    clock_frequency
    current_channel
    channel_max
    channels_used
    elapsed_real_time
    preset_real_time
    dwell_time
    prescale
    acquiring
    acquire_mode
    model
    firmware
    channel_advance
    count_on_start
    software_channel_advance
    channel1_source
    user_led
    mux_output
    input_mode
    output_mode
    output_polarity
    read_rate
    do_read_all
""".split()


@pytest.mark.parametrize("name", COMPONENT_NAMES)
def test_component_names_exist(name):
    device = Struck3820("phony:epics:name:", name="device")
    assert name in device.component_names
