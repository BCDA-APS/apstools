
"""
Ophyd support for the EPICS epid record


Public Structures

.. autosummary::
   
    ~EpidRecord

:see: https://epics.anl.gov/bcda/synApps/std/epidRecord.html
"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2019, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

from ophyd.device import Component
from ophyd import EpicsSignal, EpicsSignalRO
from ._common import EpicsRecordDeviceCommonAll
from ._common import EpicsRecordFloatFields


__all__ = ["EpidRecord", ]


class EpidRecord(EpicsRecordFloatFields, EpicsRecordDeviceCommonAll):
    """
    EPICS epid record support in ophyd
    
    :see: https://epics.anl.gov/bcda/synApps/std/epidRecord.html
    """
    controlled_value_link = Component(EpicsSignal, ".INP")
    controlled_value = Component(EpicsSignalRO, ".CVAL")

    readback_trigger_link = Component(EpicsSignal, ".TRIG")
    readback_trigger_link_value = Component(EpicsSignal, ".TVAL")

    setpoint_location = Component(EpicsSignal, ".STPL")
    setpoint_mode_select = Component(EpicsSignal, ".SMSL")

    output_location = Component(EpicsSignal, ".OUTL")
    feedback_on = Component(EpicsSignal, ".FBON")

    proportional_gain = Component(EpicsSignal, ".KP")
    integral_gain = Component(EpicsSignal, ".KI")
    derivative_gain = Component(EpicsSignal, ".KD")

    following_error = Component(EpicsSignalRO, ".ERR")
    output_value = Component(EpicsSignalRO, ".OVAL")

    calculated_P = Component(EpicsSignalRO, ".P")
    calculated_I = Component(EpicsSignal, ".I")
    calculated_D = Component(EpicsSignalRO, ".D")

    clock_ticks = Component(EpicsSignalRO, ".CT")
    time_difference = Component(EpicsSignal, ".DT")
    minimum_delta_time = Component(EpicsSignal, ".MDT")

    # limits imposed by the record support:
    #     .LOPR <= .OVAL <= .HOPR
    #     .LOPR <= .I <= .HOPR
    high_limit = Component(EpicsSignal, ".DRVH")
    low_limit = Component(EpicsSignal, ".DRVL")

    @property
    def value(self):
        return self.output_value.value
