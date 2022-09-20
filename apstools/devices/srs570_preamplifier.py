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

from ophyd import Component
from ophyd import EpicsSignal
from .preamp_base import PreamplifierBaseDevice

import logging
import pint

logger = logging.getLogger(__name__)


class SRS570_PreAmplifier(PreamplifierBaseDevice):
    """
    Ophyd support for Stanford Research Systems 570 preamplifier from synApps.
    """

    # These values are strings because that is how they are defined
    # in the EPICS .db file.  Must cast them to ``float()`` or ``int()``
    # as desired.
    # see: https://github.com/epics-modules/ip/blob/master/ipApp/Db/SR570.db
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
    def computed_gain(self):
        """
        Amplifier gain (A/V), as floating-point number.
        """
        return pint.Quantity(
            float(self.sensitivity_value.get()),
            self.sensitivity_unit.get()
        ).to("A/V").magnitude

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
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
