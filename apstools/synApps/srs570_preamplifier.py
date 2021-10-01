"""
Ophyd support for Stanford Research Systems 570 preamplifier from synApps

Public Structures

.. autosummary::

    ~SRS570_PreAmplifier

:see: https://github.com/epics-modules/ip
"""

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2021, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

__all__ = [
    "SRS570_PreAmplifier",
]

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
import logging

logger = logging.getLogger(__name__)


class SRS570_PreAmplifier(Device):
    """
    Ophyd support for Stanford Research Systems 570 preamplifier from synApps.
    """

    # TODO: why is this a string?
    sensitivity_value = Component(EpicsSignal, "sens_num", kind="config", string=True)
    sensitivity_unit = Component(EpicsSignal, "sens_unit", kind="config", string=True)

    offset_on = Component(EpicsSignal, "offset_on", kind="config", string=True)
    offset_sign = Component(EpicsSignal, "offset_sign", kind="config", string=True)
    offset_value = Component(EpicsSignal, "offset_num", kind="config", string=True)
    offset_unit = Component(EpicsSignal, "offset_unit", kind="config", string=True)
    offset_fine = Component(EpicsSignal, "off_u_put", kind="config", string=True)
    offset_cal = Component(EpicsSignal, "offset_cal", kind="config", string=True)

    set_all = Component(EpicsSignal, "init.PROC", kind="config")

    bias_value = Component(EpicsSignal, "bias_put", kind="config", string=True)
    bias_on = Component(EpicsSignal, "bias_on", kind="config", string=True)

    filter_type = Component(EpicsSignal, "filter_type", kind="config", string=True)
    filter_lowpass = Component(EpicsSignal, "low_freq", kind="config", string=True)
    filter_highpass = Component(EpicsSignal, "high_freq", kind="config", string=True)

    gain_mode = Component(EpicsSignal, "gain_mode", kind="config", string=True)
    invert = Component(EpicsSignal, "invert_on", kind="config", string=True)
    blank = Component(EpicsSignal, "blank_on", kind="config", string=True)

    @property
    def gain(self):
        """
        Return amplifier's current setting of gain, including sensitivity.
        """
        # FIXME: self.sensitivity_value.get() is a string
        raise NotImplementedError("Must test with REAL SRS570 here.")
        # enums = self.sensitivity_value.enum_strs
        # sensitivity_index = self.sensitivity_value.get()
        # sensitivity = float(enums[sensitivity_index])

        # gain = {
        #     "mA/V": 1e-3,
        #     "uA/V": 1e-6,
        #     "nA/V": 1e-9,
        #     "pA/V": 1e-12,
        # }[self.sensitivity_unit.get()]

        # return gain * sensitivity
