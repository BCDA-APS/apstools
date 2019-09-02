
#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2019, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

"""
Ophyd support for fields common to all EPICS records


Public Structures

.. autosummary::
   
    ~EpicsRecordDeviceCommonAll
    ~EpicsRecordInputFields
    ~EpicsRecordOutputFields
    ~EpicsRecordFloatFields

:see: https://wiki-ext.aps.anl.gov/epics/index.php/RRM_3-14_dbCommon
:see: https://wiki-ext.aps.anl.gov/epics/index.php/RRM_3-14_Common
"""

from ophyd.device import Device, Component
from ophyd import EpicsSignal, EpicsSignalRO


__all__ = [
    "EpicsRecordDeviceCommonAll", 
    "EpicsRecordInputFields",
    "EpicsRecordOutputFields",
    "EpicsRecordFloatFields",
    ]


class EpicsRecordDeviceCommonAll(Device):
    """
    Many of the field common to all EPICS records
    
    Some fields are not included because they are not interesting to
    an EPICS client or are already provided in other support.
    """
    description = Component(EpicsSignal, ".DESC")
    processing_active = Component(EpicsSignalRO, ".PACT")
    scanning_rate = Component(EpicsSignal, ".SCAN")
    disable_value = Component(EpicsSignal, ".DISV")
    scan_disable_input_link_value = Component(EpicsSignal, ".DISA")
    scan_disable_value_input_link = Component(EpicsSignal, ".SDIS")
    process_record = Component(EpicsSignal, ".PROC")
    forward_link = Component(EpicsSignal, ".FLNK")
    trace_processing = Component(EpicsSignal, ".TPRO")
    device_type = Component(EpicsSignalRO, ".DTYP")

    alarm_status = Component(EpicsSignalRO, ".STAT")
    alarm_severity = Component(EpicsSignalRO, ".SEVR")
    new_alarm_status = Component(EpicsSignalRO, ".NSTA")
    new_alarm_severity = Component(EpicsSignalRO, ".NSEV")
    disable_alarm_severity = Component(EpicsSignal, ".DISS")


class EpicsRecordInputFields(Device):
    """
    some fields common to EPICS input records
    """
    input_link = Component(EpicsSignal, ".INP")
    raw_value = Component(EpicsSignal, ".RVAL")
    final_value = Component(EpicsSignal, ".VAL")
    
    # will ignore simulation mode fields
    
    @property
    def value(self):
        return self.final_value.value


class EpicsRecordOutputFields(Device):
    """
    some fields common to EPICS output records
    """
    output_link = Component(EpicsSignal, ".OUT")
    raw_value = Component(EpicsSignal, ".RVAL")
    output_value = Component(EpicsSignal, ".OVAL")
    readback_value = Component(EpicsSignalRO, ".RBV")
    desired_output_location = Component(EpicsSignal, ".DOL")
    output_mode_select = Component(EpicsSignal, ".OMSL")
    desired_value = Component(EpicsSignal, ".VAL")
    
    # will ignore simulation mode fields
    
    @property
    def value(self):
        return self.desired_value.value


class EpicsRecordFloatFields(Device):
    """
    some fields common to EPICS records supporting floating point values
    """
    units = Component(EpicsSignal, ".EGU")
    precision = Component(EpicsSignal, ".PREC")

    monitor_deadband = Component(EpicsSignal, ".MDEL")

    # upper and lower display limits for the VAL, CVAL, HIHI, HIGH, LOW, and LOLO fields
    high_operating_range = Component(EpicsSignal, ".HOPR")
    low_operating_range = Component(EpicsSignal, ".LOPR")
    
    hihi_alarm_limit = Component(EpicsSignal, ".HIHI")
    high_alarm_limit = Component(EpicsSignal, ".HIGH")
    low_alarm_limit = Component(EpicsSignal, ".LOW")
    lolo_alarm_limit = Component(EpicsSignal, ".LOLO")
    hihi_alarm_severity = Component(EpicsSignal, ".HHSV")
    high_alarm_severity = Component(EpicsSignal, ".HSV")
    low_alarm_severity = Component(EpicsSignal, ".LSV")
    lolo_alarm_severity = Component(EpicsSignal, ".LLSV")
    alarm_hysteresis = Component(EpicsSignal, ".HYST")
