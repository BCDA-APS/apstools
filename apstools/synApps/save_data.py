"""
Ophyd support for the EPICS synApps saveData support

see:  https://epics.anl.gov/bcda/synApps/sscan/sscanRecord.html

EXAMPLE

    from apstools.synApps import SaveData
    save_data = SaveData("xxx:saveData_", name="save_data")


Public Structures

.. autosummary::

    ~SaveData

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


from ophyd import Device, Component, EpicsSignal, EpicsSignalRO

__all__ = [
    "SaveData",
]


class SaveData(Device):
    """
    EPICS synApps saveData support

    .. index:: Ophyd Device; synApps SaveData

    usage::

        from apstools.synApps import SaveData
        save_data = SaveData("xxx:saveData_", name="save_data")

    .. autosummary::

        ~reset

    """

    file_system = Component(EpicsSignal, "fileSystem")
    subdirectory = Component(EpicsSignal, "subDir")
    base_name = Component(EpicsSignal, "baseName")
    next_scan_number = Component(EpicsSignal, "scanNumber")
    comment1 = Component(EpicsSignal, "comment1", string=True)
    comment2 = Component(EpicsSignal, "comment2", string=True)
    write_1D_each_point = Component(EpicsSignal, "realTime1D", string=True)
    max_retries = Component(EpicsSignal, "maxAllowedRetries")
    retry_wait_s = Component(EpicsSignal, "retryWaitinSecs")

    full_path_name = Component(EpicsSignalRO, "fullPathName", string=True)
    full_name = Component(EpicsSignalRO, "fileName", string=True)
    message = Component(EpicsSignalRO, "message", string=True)
    status = Component(EpicsSignalRO, "status", string=True)
    write_count_current = Component(EpicsSignalRO, "currRetries")
    write_count_total = Component(EpicsSignalRO, "totalRetries")
    write_count_abandoned = Component(EpicsSignalRO, "abandonedWrites")

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
