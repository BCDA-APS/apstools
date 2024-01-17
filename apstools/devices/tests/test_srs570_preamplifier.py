import pytest
from unittest import mock

from apstools.devices.srs570_preamplifier import SRS570_PreAmplifier, GainSignal, DEFAULT_WRITE_TIMEOUT

# Known settling times measured from the I0 SR-570 at 25-ID-C
settling_times = {
    # (sensitivity_value, sensitivity_unit, gain_mode): settle_time
    # pA/V
    (0, 0, "HIGH BW"): 2,
    (1, 0, "HIGH BW"): 1.75,
    (2, 0, "HIGH BW"): 1.5,
    (3, 0, "HIGH BW"): 0.75,
    (4, 0, "HIGH BW"): 0.3,
    (5, 0, "HIGH BW"): 0.3,
    (6, 0, "HIGH BW"): 0.3,
    (7, 0, "HIGH BW"): 0.2,
    (8, 0, "HIGH BW"): 0.2,
    # nA/V
    (0, 1, "HIGH BW"): 0.2,
    (1, 1, "HIGH BW"): 0.2,
    (2, 1, "HIGH BW"): 0.2,
    (3, 1, "HIGH BW"): 0.2,
    (4, 1, "HIGH BW"): 0.2,
    (5, 1, "HIGH BW"): 0.2,
    (6, 1, "HIGH BW"): 0.2,
    (7, 1, "HIGH BW"): 0.2,
    (8, 1, "HIGH BW"): 0.2,
    # μA/V
    (0, 2, "HIGH BW"): 0.15,
    (1, 2, "HIGH BW"): 0.15,
    (2, 2, "HIGH BW"): 0.15,
    (3, 2, "HIGH BW"): 0.15,
    (4, 2, "HIGH BW"): 0.15,
    (5, 2, "HIGH BW"): 0.15,
    (6, 2, "HIGH BW"): 0.15,
    (7, 2, "HIGH BW"): 0.15,
    (8, 2, "HIGH BW"): 0.15,
    # mA/V
    (0, 3, "HIGH BW"): 0.15,
    (1, 3, "HIGH BW"): None,
    (2, 3, "HIGH BW"): None,
    (3, 3, "HIGH BW"): None,
    (4, 3, "HIGH BW"): None,
    (5, 3, "HIGH BW"): None,
    (6, 3, "HIGH BW"): None,
    (7, 3, "HIGH BW"): None,
    (8, 3, "HIGH BW"): None,
    # pA/V
    (0, 0, "LOW NOISE"): 2.0,
    (1, 0, "LOW NOISE"): 1.75,
    (2, 0, "LOW NOISE"): 1.5,
    (3, 0, "LOW NOISE"): 1.25,
    (4, 0, "LOW NOISE"): 1.0,
    (5, 0, "LOW NOISE"): 1.0,
    (6, 0, "LOW NOISE"): 1.0,
    (7, 0, "LOW NOISE"): 0.3,
    (8, 0, "LOW NOISE"): 0.3,
    # nA/V
    (0, 1, "LOW NOISE"): 0.3,
    (1, 1, "LOW NOISE"): 0.2,
    (2, 1, "LOW NOISE"): 0.2,
    (3, 1, "LOW NOISE"): 0.2,
    (4, 1, "LOW NOISE"): 0.2,
    (5, 1, "LOW NOISE"): 0.2,
    (6, 1, "LOW NOISE"): 0.2,
    (7, 1, "LOW NOISE"): 0.2,
    (8, 1, "LOW NOISE"): 0.2,
    # μA/V
    (0, 2, "LOW NOISE"): 0.15,
    (1, 2, "LOW NOISE"): 0.15,
    (2, 2, "LOW NOISE"): 0.15,
    (3, 2, "LOW NOISE"): 0.15,
    (4, 2, "LOW NOISE"): 0.15,
    (5, 2, "LOW NOISE"): 0.15,
    (6, 2, "LOW NOISE"): 0.15,
    (7, 2, "LOW NOISE"): 0.15,
    (8, 2, "LOW NOISE"): 0.15,
    # mA/V
    (0, 3, "LOW NOISE"): 0.15,
    (1, 3, "LOW NOISE"): None,
    (2, 3, "LOW NOISE"): None,
    (3, 3, "LOW NOISE"): None,
    (4, 3, "LOW NOISE"): None,
    (5, 3, "LOW NOISE"): None,
    (6, 3, "LOW NOISE"): None,
    (7, 3, "LOW NOISE"): None,
    (8, 3, "LOW NOISE"): None,
}

gain_units = ["pA/V", "nA/V", "uA/V", "mA/V"]
gain_values = ["1", "2", "5", "10", "20", "50", "100", "200", "500"]
gain_modes = ["LOW NOISE", "HIGH BW"]


@pytest.mark.parametrize("gain_mode", gain_modes)
@pytest.mark.parametrize("gain_unit", gain_units)
@pytest.mark.parametrize("gain_value", gain_values)
@mock.patch("apstools.devices.srs570_preamplifier.EpicsSignal.set")
def test_preamp_gain_settling(mocked_setter, gain_value, gain_unit, gain_mode):
    """The SR-570 Pre-amp voltage spikes when changing gain.

    One solution, tested here, is to add a dynamic settling time.

    """
    value_idx = gain_values.index(gain_value)
    unit_idx = gain_units.index(gain_unit)
    settle_time = settling_times[
        (
            value_idx,
            unit_idx,
            gain_mode,
        )
    ]
    # We need a real pre-amp device otherwise .set isn't in the MRO
    preamp = SRS570_PreAmplifier("prefix:", name="preamp")
    assert isinstance(preamp.sensitivity_unit, GainSignal)
    assert isinstance(preamp.sensitivity_value, GainSignal)
    status = preamp.sensitivity_unit.get = mock.MagicMock(return_value=gain_unit)
    status = preamp.gain_mode.get = mock.MagicMock(return_value=gain_mode)
    # Set the sensitivity based on value
    status = preamp.sensitivity_value.set(gain_value)
    # Check that the EpicsSignal's ``set`` was called with correct settle_time
    mocked_setter.assert_called_with(gain_value, timeout=DEFAULT_WRITE_TIMEOUT, settle_time=settle_time)
    # Set the sensitivity based on value
    mocked_setter.reset_mock()
    assert not mocked_setter.called
    status = preamp.sensitivity_value.set(value_idx)
    # Check that the EpicsSignal's ``set`` was called with correct settle_time
    mocked_setter.assert_called_with(value_idx, timeout=DEFAULT_WRITE_TIMEOUT, settle_time=settle_time)


@mock.patch("apstools.devices.srs570_preamplifier.EpicsSignal.set")
def test_preamp_gain_mode_settling(mocked_setter):
    """The SR-570 Pre-amp also has a low drift mode, whose settling
    times are the same as the low noise mode.
    """
    # We need a real pre-amp device otherwise .set isn't in the MRO
    preamp = SRS570_PreAmplifier("prefix:", name="preamp")
    gain_unit = "pA/V"
    gain_value = "500"
    settle_time = 0.3
    status = preamp.sensitivity_unit.get = mock.MagicMock(return_value=gain_unit)
    status = preamp.sensitivity_value.get = mock.MagicMock(return_value=gain_value)
    # Set the sensitivity based on value
    status = preamp.gain_mode.set("LOW DRIFT")
    # Check that the EpicsSignal's ``set`` was called with correct settle_time
    mocked_setter.assert_called_with("LOW DRIFT", timeout=DEFAULT_WRITE_TIMEOUT, settle_time=settle_time)
