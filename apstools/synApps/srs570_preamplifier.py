"""
Ophyd support for aynsApps Stanford Research Systems 570 preamplifier

Public Structures

.. autosummary::

    ~AsynRecord

:see: https://github.com/epics-modules/asyn
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

__all__ = ["SRS570_PreAmplifier", ]
from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal
import logging

logger = logging.getLogger(__name__)


class SRS570_PreAmplifier(Device):

    # Current sensitivity
    sensitivity_value = Component(
        EpicsSignal, "sens_num.VAL", kind="config", string=True
    )

    sensitivity_unit = Component(
        EpicsSignal, "sens_unit.VAL", kind="config", string=True
    )

    # Offset current
    offset_on = Component(EpicsSignal, "offset_on.VAL", kind="config", string=True)

    offset_sign = Component(EpicsSignal, "offset_sign.VAL", kind="config", string=True)

    offset_value = Component(EpicsSignal, "offset_num.VAL", kind="config", string=True)

    offset_unit = Component(EpicsSignal, "offset_unit.VAL", kind="config", string=True)

    offset_fine = Component(EpicsSignal, "off_u_put.VAL", kind="config", string=True)

    offset_cal = Component(EpicsSignal, "offset_cal.VAL", kind="config", string=True)

    # Set all button
    set_all = Component(EpicsSignal, "init.PROC", kind="config")

    # Bias voltage
    bias_value = Component(EpicsSignal, "bias_put.VAL", kind="config", string=True)

    bias_on = Component(EpicsSignal, "bias_on.VAL", kind="config", string=True)

    # Filter
    filter_type = Component(EpicsSignal, "filter_type.VAL", kind="config", string=True)

    filter_lowpass = Component(EpicsSignal, "low_freq.VAL", kind="config", string=True)

    filter_highpass = Component(
        EpicsSignal, "high_freq.VAL", kind="config", string=True
    )

    # Gain mode
    gain_mode = Component(EpicsSignal, "gain_mode.VAL", kind="config", string=True)

    # Invert
    invert = Component(EpicsSignal, "invert_on.VAL", kind="config", string=True)

    # Blank
    blank = Component(EpicsSignal, "blank_on.VAL", kind="config", string=True)
