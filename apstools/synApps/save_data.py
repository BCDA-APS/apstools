"""
Ophyd support for the EPICS synApps saveData support

see:  https://epics.anl.gov/bcda/synApps/sscan/sscanRecord.html

EXAMPLE::

    from apstools.synApps import SaveData
    save_data = SaveData("xxx:saveData_", name="save_data")


Public Structures

.. autosummary::

    ~SaveData

"""


from ophyd import Device
from ophyd import Component
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO


class SaveData(Device):
    """
    EPICS synApps saveData support.

    .. index:: Ophyd Device; synApps SaveData

    usage::

        from apstools.synApps import SaveData
        save_data = SaveData("xxx:saveData_", name="save_data")

    .. autosummary::

        ~reset

    """

    file_system = Component(EpicsSignal, "fileSystem", kind="config")
    subdirectory = Component(EpicsSignal, "subDir", kind="config")
    base_name = Component(EpicsSignal, "baseName", kind="config")
    next_scan_number = Component(EpicsSignal, "scanNumber", kind="config")
    comment1 = Component(EpicsSignal, "comment1", string=True, kind="config")
    comment2 = Component(EpicsSignal, "comment2", string=True, kind="config")
    write_1D_each_point = Component(
        EpicsSignal, "realTime1D", string=True, kind="config"
    )
    max_retries = Component(EpicsSignal, "maxAllowedRetries", kind="config")
    retry_wait_s = Component(EpicsSignal, "retryWaitinSecs", kind="config")

    full_path_name = Component(
        EpicsSignalRO, "fullPathName", string=True, kind="config"
    )
    full_name = Component(EpicsSignalRO, "fileName", string=True, kind="normal")
    message = Component(EpicsSignalRO, "message", string=True, kind="config")
    status = Component(EpicsSignalRO, "status", string=True, kind="config")
    write_count_current = Component(EpicsSignalRO, "currRetries", kind="config")
    write_count_total = Component(EpicsSignalRO, "totalRetries", kind="config")
    write_count_abandoned = Component(EpicsSignalRO, "abandonedWrites", kind="config")

    def reset(self):
        self.file_system.put("")
        self.subdirectory.put("")
        self.base_name.put("")
        self.next_scan_number.put(1)
        self.comment1.put("")
        self.comment2.put("")
        self.write_1D_each_point.put("No")
        self.max_retries.put(10)
        self.retry_wait_s.put(15)

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
