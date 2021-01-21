"""
Ophyd support for the EPICS busy record


Public Structures

.. autosummary::

    ~BusyRecord

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

from enum import Enum
from ophyd.device import Device, Component
from ophyd import EpicsSignal


__all__ = """
    BusyRecord
    BusyStatus
    """.split()


class BusyStatus(str, Enum):
    busy = "Busy"
    done = "Done"


class BusyRecord(Device):
    """
    synApps busy record

    .. index:: Ophyd Device; synApps BusyRecord
    """
    state = Component(EpicsSignal, "")
    output_link = Component(EpicsSignal, ".OUT")
    forward_link = Component(EpicsSignal, ".FLNK")
