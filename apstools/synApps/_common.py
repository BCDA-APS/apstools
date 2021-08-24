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

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2021, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

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
    Many of the fields common to all EPICS records

    Some fields are not included because they are not interesting to
    an EPICS client or are already provided in other support.
    """

    description = Component(EpicsSignal, ".DESC", kind="config")
    processing_active = Component(EpicsSignalRO, ".PACT", kind="omitted")
    scanning_rate = Component(EpicsSignal, ".SCAN", kind="config")
    disable_value = Component(EpicsSignal, ".DISV", kind="config")
    scan_disable_input_link_value = Component(EpicsSignal, ".DISA", kind="config")
    scan_disable_value_input_link = Component(EpicsSignal, ".SDIS", kind="config")
    process_record = Component(EpicsSignal, ".PROC", kind="omitted")
    forward_link = Component(EpicsSignal, ".FLNK", kind="config")
    trace_processing = Component(EpicsSignal, ".TPRO", kind="omitted")
    device_type = Component(EpicsSignalRO, ".DTYP", kind="config")

    alarm_status = Component(EpicsSignalRO, ".STAT", kind="config")
    alarm_severity = Component(EpicsSignalRO, ".SEVR", kind="config")
    new_alarm_status = Component(EpicsSignalRO, ".NSTA", kind="config")
    new_alarm_severity = Component(EpicsSignalRO, ".NSEV", kind="config")
    disable_alarm_severity = Component(EpicsSignal, ".DISS", kind="config")


class EpicsRecordInputFields(Device):
    """
    some fields common to EPICS input records
    """

    input_link = Component(EpicsSignal, ".INP", kind="config")
    raw_value = Component(EpicsSignal, ".RVAL", kind="config")
    final_value = Component(EpicsSignal, ".VAL", kind="normal")

    # will ignore simulation mode fields

    @property
    def value(self):
        return self.final_value.get()


class EpicsRecordOutputFields(Device):
    """
    some fields common to EPICS output records
    """

    output_link = Component(EpicsSignal, ".OUT", kind="config")
    raw_value = Component(EpicsSignal, ".RVAL", kind="config")
    output_value = Component(EpicsSignal, ".OVAL", kind="normal")
    readback_value = Component(EpicsSignalRO, ".RBV", kind="hinted")
    desired_output_location = Component(EpicsSignal, ".DOL", kind="config")
    output_mode_select = Component(EpicsSignal, ".OMSL", kind="config")
    desired_value = Component(EpicsSignal, ".VAL", kind="normal")

    # will ignore simulation mode fields

    @property
    def value(self):
        return self.desired_value.get()


class EpicsRecordFloatFields(Device):
    """
    some fields common to EPICS records supporting floating point values
    """

    units = Component(EpicsSignal, ".EGU", kind="config")
    precision = Component(EpicsSignal, ".PREC", kind="config")

    monitor_deadband = Component(EpicsSignal, ".MDEL", kind="config")

    # upper and lower display limits for the VAL, CVAL, HIHI, HIGH, LOW, and LOLO fields
    high_operating_range = Component(EpicsSignal, ".HOPR", kind="config")
    low_operating_range = Component(EpicsSignal, ".LOPR", kind="config")

    hihi_alarm_limit = Component(EpicsSignal, ".HIHI", kind="config")
    high_alarm_limit = Component(EpicsSignal, ".HIGH", kind="config")
    low_alarm_limit = Component(EpicsSignal, ".LOW", kind="config")
    lolo_alarm_limit = Component(EpicsSignal, ".LOLO", kind="config")
    hihi_alarm_severity = Component(EpicsSignal, ".HHSV", kind="config")
    high_alarm_severity = Component(EpicsSignal, ".HSV", kind="config")
    low_alarm_severity = Component(EpicsSignal, ".LSV", kind="config")
    lolo_alarm_severity = Component(EpicsSignal, ".LLSV", kind="config")
    alarm_hysteresis = Component(EpicsSignal, ".HYST", kind="config")
