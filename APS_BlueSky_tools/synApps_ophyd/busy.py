
"""
Ophyd support for the EPICS busy record


Public Structures

.. autosummary::
   
    ~busyRecord

"""


from ophyd.device import Device, Component
from ophyd import EpicsSignal


__all__ = """
    busyRecord
    """.split()


class busyRecord(Device):
    state = Component(EpicsSignal, "")
    output_link = Component(EpicsSignal, ".OUT")
    forward_link = Component(EpicsSignal, ".FLNK")
