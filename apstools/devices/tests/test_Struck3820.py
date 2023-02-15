import pytest

from ..struck3820 import Struck3820

COMPONENT_NAMES = """
    acquire_mode
    acquiring
    channel_advance
    channel_max
    channel1_source
    channels_used
    clock_frequency
    count_on_start
    current_channel
    do_read_all
    dwell_time
    elapsed_real_time
    erase_all
    erase_start
    firmware
    input_mode
    mca1
    mca2
    mca3
    mca4
    model
    mux_output
    output_mode
    output_polarity
    prescale
    preset_real_time
    read_rate
    software_channel_advance
    start_all
    stop_all
    user_led
""".split()


@pytest.mark.parametrize("name", COMPONENT_NAMES)
def test_component_names_exist(name):
    device = Struck3820("phony:epics:name:", name="device")
    assert name in device.component_names
