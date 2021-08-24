"""
Ophyd support for the EPICS epid record


Public Structures

.. autosummary::

    ~EpidRecord

:see: https://epics.anl.gov/bcda/synApps/std/epidRecord.html
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

from ophyd.device import Component
from ophyd import EpicsSignal, EpicsSignalRO
from ._common import EpicsRecordDeviceCommonAll
from ._common import EpicsRecordFloatFields


__all__ = [
    "EpidRecord",
]


class EpidRecord(EpicsRecordFloatFields, EpicsRecordDeviceCommonAll):
    """
    EPICS epid record support in ophyd

    .. index:: Ophyd Device; synApps EpidRecord

    :see: https://epics.anl.gov/bcda/synApps/std/epidRecord.html
    """

    controlled_value_link = Component(EpicsSignal, ".INP", kind="config")
    controlled_value = Component(EpicsSignalRO, ".CVAL", kind="config")

    readback_trigger_link = Component(EpicsSignal, ".TRIG", kind="config")
    readback_trigger_link_value = Component(EpicsSignal, ".TVAL", kind="config")

    setpoint_location = Component(EpicsSignal, ".STPL", kind="config")
    setpoint_mode_select = Component(EpicsSignal, ".SMSL", kind="config")

    output_location = Component(EpicsSignal, ".OUTL", kind="config")
    feedback_on = Component(EpicsSignal, ".FBON", kind="config")

    proportional_gain = Component(EpicsSignal, ".KP", kind="config")
    integral_gain = Component(EpicsSignal, ".KI", kind="config")
    derivative_gain = Component(EpicsSignal, ".KD", kind="config")

    following_error = Component(EpicsSignalRO, ".ERR", kind="config")
    output_value = Component(EpicsSignalRO, ".OVAL", kind="config")
    final_value = Component(EpicsSignalRO, ".VAL", kind="normal")

    calculated_P = Component(EpicsSignalRO, ".P", kind="config")
    calculated_I = Component(EpicsSignal, ".I", kind="config")
    calculated_D = Component(EpicsSignalRO, ".D", kind="config")

    time_difference = Component(EpicsSignal, ".DT", kind="config")
    minimum_delta_time = Component(EpicsSignal, ".MDT", kind="config")

    # limits imposed by the record support:
    #     .LOPR <= .OVAL <= .HOPR
    #     .LOPR <= .I <= .HOPR
    high_limit = Component(EpicsSignal, ".DRVH", kind="config")
    low_limit = Component(EpicsSignal, ".DRVL", kind="config")

    @property
    def value(self):
        return self.output_value.get()
