"""
Ophyd support for Stanford Research Systems 570 preamplifier from synApps

Public Structures

.. autosummary::

    ~SRS570_PreAmplifier

This device connects with the SRS570 support from synApps.
(https://github.com/epics-modules/ip/blob/master/ipApp/Db/SR570.db)

The SRS570 synApps support is part of the ``ip`` module:
https://htmlpreview.github.io/?https://raw.githubusercontent.com/epics-modules/ip/R3-6-1/documentation/swaitRecord.html

:see: https://github.com/epics-modules/ip
"""

import logging

import pint
from ophyd import Component
from ophyd import EpicsSignal
from ophyd.signal import DEFAULT_WRITE_TIMEOUT

from .preamp_base import PreamplifierBaseDevice

logger = logging.getLogger(__name__)


gain_units = ["pA/V", "nA/V", "uA/V", "mA/V"]
gain_values = ["1", "2", "5", "10", "20", "50", "100", "200", "500"]
gain_modes = ["LOW NOISE", "HIGH BW"]

# Settling times measured from the 25-ID-C upstream I0 chamber's SR-570
# (sensitivity_value, sensitivity_unit, gain_mode): settle_time
settling_times = {
    # pA/V
    ("1", "pA/V", "HIGH BW"): 2.5,
    ("2", "pA/V", "HIGH BW"): 2,
    ("5", "pA/V", "HIGH BW"): 2.0,
    ("10", "pA/V", "HIGH BW"): 0.5,
    ("20", "pA/V", "HIGH BW"): 0.5,
    ("50", "pA/V", "HIGH BW"): 0.5,
    ("100", "pA/V", "HIGH BW"): 0.5,
    ("200", "pA/V", "HIGH BW"): 0.3,
    ("500", "pA/V", "HIGH BW"): 0.3,
    ("1", "pA/V", "LOW NOISE"): 3.0,
    ("2", "pA/V", "LOW NOISE"): 2.5,
    ("5", "pA/V", "LOW NOISE"): 2.0,
    ("10", "pA/V", "LOW NOISE"): 2.0,
    ("20", "pA/V", "LOW NOISE"): 1.75,
    ("50", "pA/V", "LOW NOISE"): 1.5,
    ("100", "pA/V", "LOW NOISE"): 1.25,
    ("200", "pA/V", "LOW NOISE"): 0.5,
    ("500", "pA/V", "LOW NOISE"): 0.5,
}
settling_times.update(
    {
        # nA/V, high bandwidth
        (gain_values[idx], "nA/V", "HIGH BW"): 0.3
        for idx in range(9)
    }
)
settling_times.update(
    {
        # nA/V, low noise
        (gain_values[idx], "nA/V", "LOW NOISE"): 0.3
        for idx in range(9)
    }
)
settling_times.update(
    {
        # μA/V, high bandwidth
        (gain_values[idx], "uA/V", "HIGH BW"): 0.3
        for idx in range(9)
    }
)
settling_times.update(
    {
        # μA/V, low noise
        (gain_values[idx], "uA/V", "LOW NOISE"): 0.3
        for idx in range(9)
    }
)
settling_times.update(
    {
        ("1", "mA/V", "HIGH BW"): 0.3,
        ("1", "mA/V", "LOW NOISE"): 0.3,
    }
)


def calculate_settle_time(gain_value: int, gain_unit: int, gain_mode: str):
    """Determine the best settle time for a given combination of parameters.

    Parameters can be strings of indexes.

    """
    # Convert indexes to string values
    try:
        gain_value = gain_values[gain_value]
    except (TypeError, IndexError):
        pass
    try:
        gain_unit = gain_units[gain_unit]
    except (TypeError, IndexError):
        pass
    try:
        gain_mode = gain_modes[gain_mode]
    except (TypeError, IndexError):
        pass
    # Get calibrated settle time, or None to use the Ophyd default
    return settling_times.get((gain_value, gain_unit, gain_mode))


class GainSignal(EpicsSignal):
    """
    A signal where the settling time depends on the pre-amp gain.

    Used to introduce a specific settle time when setting to account
    for the amp's RC relaxation time when changing gain.
    """

    def set(self, value, *, timeout=DEFAULT_WRITE_TIMEOUT, settle_time="auto"):
        """
        Set the value of the Signal and return a Status object.

        If put completion is used for this EpicsSignal, the status object
        will complete once EPICS reports the put has completed.

        Otherwise the readback will be polled until equal to the set point
        (as in ``Signal.set``)

        Parameters
        ----------

        value : any
            The gain value.

        timeout : float, optional
            Maximum time to wait.

        settle_time: float, optional
            Delay after ``set()`` has completed to indicate completion
            to the caller. If ``"auto"`` (default), a reasonable settle
            time will be chosen based on the gain mode of the pre-amp.

        Returns
        -------
        st : Status

        .. seealso::
            * Signal.set
            * EpicsSignal.set

        """
        # Determine optimal settling time.
        if settle_time == "auto":
            signals = [self.parent.sensitivity_value, self.parent.sensitivity_unit, self.parent.gain_mode]
            args = [value if self is sig else sig.get() for sig in signals]
            val, unit, mode = args
            # Resolve string values to indices if provided
            if val in gain_values:
                val = gain_values.index(val)
            if unit in gain_units:
                unit = gain_units.index(unit)
            if mode in gain_modes:
                mode = gain_modes.index(mode)
            # Low-drift mode uses the same settling times as low-noise mode
            if mode == "LOW DRIFT":
                mode = "LOW NOISE"
            # Calculate settling time
            _settle_time = calculate_settle_time(gain_value=val, gain_unit=unit, gain_mode=mode)
        else:
            _settle_time = settle_time
        return super().set(value, timeout=timeout, settle_time=_settle_time)


class SRS570_PreAmplifier(PreamplifierBaseDevice):
    """
    Ophyd support for Stanford Research Systems 570 preamplifier from synApps.
    """

    # These values are strings because that is how they are defined
    # in the EPICS .db file.  Must cast them to ``float()`` or ``int()``
    # as desired.
    # see: https://github.com/epics-modules/ip/blob/master/ipApp/Db/SR570.db
    sensitivity_value = Component(GainSignal, "sens_num", kind="config", string=True)
    sensitivity_unit = Component(GainSignal, "sens_unit", kind="config", string=True, put_complete=True)

    offset_on = Component(EpicsSignal, "offset_on", kind="config", string=True)
    offset_sign = Component(EpicsSignal, "offset_sign", kind="config", string=True)
    offset_value = Component(EpicsSignal, "offset_num", kind="config", string=True)
    offset_unit = Component(EpicsSignal, "offset_unit", kind="config", string=True)
    offset_fine = Component(EpicsSignal, "off_u_put", kind="config", string=True)
    offset_cal = Component(EpicsSignal, "offset_cal", kind="config", string=True)

    set_all = Component(GainSignal, "init.PROC", kind="config")

    bias_value = Component(EpicsSignal, "bias_put", kind="config", string=True)
    bias_on = Component(EpicsSignal, "bias_on", kind="config", string=True)

    filter_type = Component(EpicsSignal, "filter_type", kind="config", string=True)
    filter_lowpass = Component(EpicsSignal, "low_freq", kind="config", string=True)
    filter_highpass = Component(EpicsSignal, "high_freq", kind="config", string=True)

    gain_mode = Component(GainSignal, "gain_mode", kind="config", string=True)
    invert = Component(EpicsSignal, "invert_on", kind="config", string=True)
    blank = Component(EpicsSignal, "blank_on", kind="config", string=True)

    @property
    def computed_gain(self):
        """
        Amplifier gain (A/V), as floating-point number.
        """
        return pint.Quantity(float(self.sensitivity_value.get()), self.sensitivity_unit.get()).to("A/V").magnitude

    def cb_gain(self, *args, **kwargs):
        """
        Called when sensitivity changes (EPICS CA monitor event).
        """
        self.gain.put(self.computed_gain)

    def __init__(self, *args, **kwargs):
        """
        Update the gain when the sensitivity changes.
        """
        super().__init__(*args, **kwargs)
        self.sensitivity_value.subscribe(self.cb_gain)
        self.sensitivity_unit.subscribe(self.cb_gain)

        # amplifier gain is the most relevant value
        self.gain.name = self.name


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
