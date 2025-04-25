"""Test the Labjack T-series data acquisition device support

Hardware is not available so test with best efforts

"""
import pytest

from ...tests import IOC_GP
from .. import labjack

PV_PREFIX = f"phony:{IOC_GP}LJT7:"


@pytest.fixture()
def labjack_device(request):
    """Parameterized fixture for creating a Vortex device with difference
    electronics support.

    """
    # Figure out which detector we're using
    device = request.getfixturevalue(request.param)
    yield device


def test_base_signals_device():
    """Test signals shared by all labjack devices."""
    t7 = labjack.LabJackBase(PV_PREFIX, name="labjack_T7")
    assert not t7.connected

    cfg_names = [
        "model_name",
        "firmware_version",
        "serial_number",
        "device_temperature",
        "ljm_version",
        "driver_version",
        "last_error_message",
        "poll_sleep_ms",
        "analog_in_settling_time_all",
        "analog_in_resolution_all",
        "analog_in_sampling_rate",
        "analog_outputs",
        "analog_outputs.ao0",
        "analog_outputs.ao0.alarm_severity",
        "analog_outputs.ao0.alarm_status",
        "analog_outputs.ao0.description",
        "analog_outputs.ao0.desired_output_location",
        "analog_outputs.ao0.device_type",
        "analog_outputs.ao0.disable_alarm_severity",
        "analog_outputs.ao0.disable_value",
        "analog_outputs.ao0.forward_link",
        "analog_outputs.ao0.new_alarm_severity",
        "analog_outputs.ao0.new_alarm_status",
        "analog_outputs.ao0.output_link",
        "analog_outputs.ao0.output_mode_select",
        "analog_outputs.ao0.raw_value",
        "analog_outputs.ao0.scan_disable_input_link_value",
        "analog_outputs.ao0.scan_disable_value_input_link",
        "analog_outputs.ao0.scanning_rate",
        "analog_outputs.ao1",
        "analog_outputs.ao1.alarm_severity",
        "analog_outputs.ao1.alarm_status",
        "analog_outputs.ao1.description",
        "analog_outputs.ao1.desired_output_location",
        "analog_outputs.ao1.device_type",
        "analog_outputs.ao1.disable_alarm_severity",
        "analog_outputs.ao1.disable_value",
        "analog_outputs.ao1.forward_link",
        "analog_outputs.ao1.new_alarm_severity",
        "analog_outputs.ao1.new_alarm_status",
        "analog_outputs.ao1.output_link",
        "analog_outputs.ao1.output_mode_select",
        "analog_outputs.ao1.raw_value",
        "analog_outputs.ao1.scan_disable_input_link_value",
        "analog_outputs.ao1.scan_disable_value_input_link",
        "analog_outputs.ao1.scanning_rate",
    ]
    assert sorted(t7.configuration_attrs) == sorted(cfg_names)

    # List all the components
    # cpt_names = [
    # ]
    # assert sorted(t7.component_names) == sorted(cpt_names)


ai_params = [
    # (model, number of analog inputs)
    (labjack.LabJackT4, 12),
    (labjack.LabJackT7, 14),
    (labjack.LabJackT7Pro, 14),
    (labjack.LabJackT8, 8),
]


@pytest.mark.parametrize("LabJackDevice,num_ais", ai_params)
def test_analog_inputs(LabJackDevice, num_ais):
    """Test analog inputs for different device types."""
    device = LabJackDevice(PV_PREFIX, name="labjack_T")
    assert not device.connected
    assert hasattr(device, "analog_inputs")
    # Check that the individual AI devices were created
    for n in range(num_ais):
        assert hasattr(device.analog_inputs, f"ai{n}")
        ai = getattr(device.analog_inputs, f"ai{n}")
        assert isinstance(ai, labjack.AnalogInput)
    # Make sure there aren't any extra analog inputs
    assert not hasattr(device.analog_inputs, f"ai{num_ais}")
    # Check read attrs
    read_attrs = ["final_value"]
    for n in range(num_ais):
        for attr in read_attrs:
            full_attr = f"analog_inputs.ai{n}.{attr}"
            assert full_attr in device.read_attrs
    # Check configuration attrs
    cfg_attrs = ["differential", "high", "low", "temperature_units", "resolution", "range", "mode", "enable"]
    for n in range(num_ais):
        for attr in cfg_attrs:
            full_attr = f"analog_inputs.ai{n}.{attr}"
            assert full_attr in device.configuration_attrs


ao_params = [
    # (model, number of analog outputs)
    (labjack.LabJackT4, 2),
    (labjack.LabJackT7, 2),
    (labjack.LabJackT7Pro, 2),
    (labjack.LabJackT8, 2),
]


@pytest.mark.parametrize("LabJackDevice,num_aos", ao_params)
def test_analog_outputs(LabJackDevice, num_aos):
    """Test analog inputs for different device types."""
    device = LabJackDevice(PV_PREFIX, name="labjack_T")
    assert not device.connected
    assert hasattr(device, "analog_outputs")
    # Check that the individual AI devices were created
    for n in range(num_aos):
        assert hasattr(device.analog_outputs, f"ao{n}")
        ai = getattr(device.analog_outputs, f"ao{n}")
        assert isinstance(ai, labjack.AnalogOutput)
    # Check read attrs
    read_attrs = ["desired_value"]
    for n in range(num_aos):
        for attr in read_attrs:
            full_attr = f"analog_outputs.ao{n}.{attr}"
            assert full_attr in device.read_attrs
    # Check configuration attrs
    cfg_attrs = ["output_mode_select"]
    for n in range(num_aos):
        for attr in cfg_attrs:
            full_attr = f"analog_outputs.ao{n}.{attr}"
            assert full_attr in device.configuration_attrs
    # Check hinted attrs
    hinted_attrs = ["readback_value"]
    for n in range(num_aos):
        for attr in hinted_attrs:
            full_attr = f"labjack_T_analog_outputs_ao{n}_{attr}"
            assert full_attr in device.hints["fields"]


dio_params = [
    # (model, number of digital I/Os)
    (labjack.LabJackT4, 16),
    (labjack.LabJackT7, 23),
    (labjack.LabJackT7Pro, 23),
    (labjack.LabJackT8, 20),
]


@pytest.mark.parametrize("LabJackDevice,num_dios", dio_params)
def test_digital_dios(LabJackDevice, num_dios):
    """Test analog inputs for different device types."""
    device = LabJackDevice(PV_PREFIX, name="labjack_T")
    assert not device.connected
    assert hasattr(device, "digital_ios")
    # Check that the individual digital I/O devices were created
    for n in range(num_dios):
        assert hasattr(device.digital_ios, f"dio{n}")
        dio = getattr(device.digital_ios, f"dio{n}")
        assert isinstance(dio, labjack.DigitalIO)
    # Check read attrs
    read_attrs = ["output.desired_value", "input.final_value"]
    for n in range(num_dios):
        for attr in read_attrs:
            full_attr = f"digital_ios.dio{n}.{attr}"
            assert full_attr in device.read_attrs
    # Check configuration attrs
    cfg_attrs = ["output.raw_value", "input.raw_value", "direction"]
    for n in range(num_dios):
        for attr in cfg_attrs:
            full_attr = f"digital_ios.dio{n}.{attr}"
            assert full_attr in device.configuration_attrs
    # Check hinted attrs
    hinted_attrs = ["output_readback_value"]
    for n in range(num_dios):
        for attr in hinted_attrs:
            full_attr = f"labjack_T_digital_ios_dio{n}_{attr}"
            assert full_attr in device.hints["fields"]


@pytest.mark.parametrize("LabJackDevice,num_dios", dio_params)
def test_digital_words(LabJackDevice, num_dios):
    """Test analog inputs for different device types."""
    device = LabJackDevice(PV_PREFIX, name="labjack_T")
    assert not device.connected
    assert hasattr(device, "digital_ios")
    # Check that the individual digital word outputs were created
    assert hasattr(device.digital_ios, "dio")
    assert hasattr(device.digital_ios, "fio")
    assert hasattr(device.digital_ios, "eio")
    assert hasattr(device.digital_ios, "cio")
    assert hasattr(device.digital_ios, "mio")
    # Check read attrs
    read_attrs = ["dio", "eio", "fio", "mio", "cio"]
    for attr in read_attrs:
        assert f"digital_ios.{attr}" in device.read_attrs


def test_waveform_digitizer():
    digitizer = labjack.WaveformDigitizer("LabJackT7_1:", name="labjack")
    assert not digitizer.connected
    # Check read attrs
    read_attrs = ["timebase_waveform", "dwell_actual", "total_time"]
    for attr in read_attrs:
        assert attr in digitizer.read_attrs
    # Check read attrs
    cfg_attrs = ["num_points", "first_chan", "num_chans", "dwell", "resolution", "settling_time", "auto_restart"]
    for attr in cfg_attrs:
        assert attr in digitizer.configuration_attrs


@pytest.mark.parametrize("LabJackDevice,num_ais", ai_params)
def test_waveform_digitizer_waveforms(LabJackDevice, num_ais):
    """Verify that the waveform digitizer is created for each LabJack."""
    device = LabJackDevice(PV_PREFIX, name="labjack_T")
    assert hasattr(device, "waveform_digitizer")
    digitizer = device.waveform_digitizer
    assert hasattr(digitizer, "waveforms")


def test_waveform_generator():
    generator = labjack.WaveformGenerator("LabJackT7_1:", name="labjack")
    assert not generator.connected
    # Check read attrs
    read_attrs = [
        "frequency",
        "dwell",
        "dwell_actual",
        "total_time",
        "user_time_waveform",
        "internal_time_waveform",
    ]
    for attr in read_attrs:
        assert attr in generator.read_attrs
    # Check read attrs
    cfg_attrs = [
        "external_trigger",
        "external_clock",
        "continuous",
        "num_points",
        "user_waveform_0",
        "enable_0",
        "type_0",
        "pulse_width_0",
        "amplitude_0",
        "offset_0",
        "user_waveform_1",
        "enable_1",
        "type_1",
        "pulse_width_1",
        "amplitude_1",
        "offset_1",
    ]
    for attr in cfg_attrs:
        assert attr in generator.configuration_attrs
