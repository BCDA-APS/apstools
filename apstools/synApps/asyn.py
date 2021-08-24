"""
Ophyd support for the EPICS asyn record

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

from ophyd.device import Component
from ophyd import EpicsSignal, EpicsSignalRO
from ._common import EpicsRecordDeviceCommonAll


__all__ = [
    "AsynRecord",
]


class AsynRecord(EpicsRecordDeviceCommonAll):
    """
    EPICS asyn record support in ophyd

    .. index:: Ophyd Device; synApps AsynRecord

    :see: https://epics.anl.gov/modules/soft/asyn/R4-36/asynRecord.html
    :see: https://github.com/epics-modules/asyn
    :see: https://epics.anl.gov/modules/soft/asyn/
    """

    ascii_output = Component(EpicsSignal, ".AOUT", kind="hinted")
    binary_output = Component(EpicsSignal, ".BOUT", kind="normal")
    end_of_message_reason = Component(EpicsSignalRO, ".EOMR", kind="config")
    input_format = Component(EpicsSignalRO, ".IFMT", kind="config")
    input_maxlength = Component(EpicsSignal, ".IMAX", kind="config")
    interface = Component(EpicsSignal, ".IFACE", kind="config")
    number_bytes_actually_read = Component(EpicsSignalRO, ".NRRD", kind="normal")
    number_bytes_actually_written = Component(EpicsSignalRO, ".NAWT", kind="normal")
    number_bytes_to_read = Component(EpicsSignal, ".NORD", kind="config")
    number_bytes_to_write = Component(EpicsSignal, ".NOWT", kind="config")
    octet_is_valid = Component(EpicsSignalRO, ".OCTETIV", kind="normal")
    output_format = Component(EpicsSignalRO, ".OFMT", kind="config")
    output_maxlength = Component(EpicsSignal, ".OMAX", kind="config")
    terminator_input = Component(EpicsSignal, ".IEOS", kind="config")
    terminator_output = Component(EpicsSignal, ".OEOS", kind="config")
    timeout = Component(EpicsSignal, ".TMOT", kind="config")
    transaction_mode = Component(EpicsSignal, ".TMOD", kind="config")
    translated_input = Component(EpicsSignal, ".TINP", kind="config")
