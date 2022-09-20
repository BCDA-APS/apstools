"""
APS Machine Parameters
+++++++++++++++++++++++++++++++++++++++

**APS machine parameters**

.. autosummary::

   ~ApsMachineParametersDevice
   ~ApsOperatorMessagesDevice
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignalRO
from .aps_cycle import ApsCycleDM


class ApsOperatorMessagesDevice(Device):
    """
    General messages from the APS main control room.

    .. index:: Ophyd Device; ApsOperatorMessagesDevice
    """

    operators = Component(EpicsSignalRO, "OPS:message1", string=True)
    floor_coordinator = Component(EpicsSignalRO, "OPS:message2", string=True)
    fill_pattern = Component(EpicsSignalRO, "OPS:message3", string=True)
    last_problem_message = Component(EpicsSignalRO, "OPS:message4", string=True)
    last_trip_message = Component(EpicsSignalRO, "OPS:message5", string=True)
    # messages 6-8: meaning?
    message6 = Component(EpicsSignalRO, "OPS:message6", string=True)
    message7 = Component(EpicsSignalRO, "OPS:message7", string=True)
    message8 = Component(EpicsSignalRO, "OPS:message8", string=True)


class ApsMachineParametersDevice(Device):
    """
    Common operational parameters of the APS of general interest.

    .. index:: Ophyd Device; ApsMachineParametersDevice

    EXAMPLE::

        import apstools.devices as APS_devices
        APS = APS_devices.ApsMachineParametersDevice(name="APS")
        aps_current = APS.current

        # make sure these values are logged at start and stop of every scan
        sd.baseline.append(APS)
        # record storage ring current as secondary stream during scans
        # name: aps_current_monitor
        # db[-1].table("aps_current_monitor")
        sd.monitors.append(aps_current)

    The `sd.baseline` and `sd.monitors` usage relies on this global setup::

        from bluesky import SupplementalData
        sd = SupplementalData()
        RE.preprocessors.append(sd)

    .. autosummary::

        ~inUserOperations

    """

    current = Component(EpicsSignalRO, "S:SRcurrentAI")
    lifetime = Component(EpicsSignalRO, "S:SRlifeTimeHrsCC")
    aps_cycle = Component(ApsCycleDM)
    machine_status = Component(EpicsSignalRO, "S:DesiredMode", string=True)
    # In [3]: APS.machine_status.enum_strs
    # Out[3]:
    # ('State Unknown',
    #  'USER OPERATIONS',
    #  'Bm Ln Studies',
    #  'INJ Studies',
    #  'ASD Studies',
    #  'NO BEAM',
    #  'MAINTENANCE')
    operating_mode = Component(EpicsSignalRO, "S:ActualMode", string=True)
    # In [4]: APS.operating_mode.enum_strs
    # Out[4]:
    # ('State Unknown',
    # 'NO BEAM',
    # 'Injecting',
    # 'Stored Beam',
    # 'Delivered Beam',
    # 'MAINTENANCE')
    shutter_permit = Component(EpicsSignalRO, "ACIS:ShutterPermit", string=True)
    fill_number = Component(EpicsSignalRO, "S:FillNumber")
    orbit_correction = Component(EpicsSignalRO, "S:OrbitCorrection:CC")
    global_feedback = Component(EpicsSignalRO, "SRFB:GBL:LoopStatusBI", string=True)
    global_feedback_h = Component(EpicsSignalRO, "SRFB:GBL:HLoopStatusBI", string=True)
    global_feedback_v = Component(EpicsSignalRO, "SRFB:GBL:VLoopStatusBI", string=True)
    operator_messages = Component(ApsOperatorMessagesDevice)

    @property
    def inUserOperations(self):
        """
        determine if APS is in User Operations mode (boolean)

        Use this property to configure ophyd Devices for direct or simulated hardware.
        See issue #49 (https://github.com/BCDA-APS/apstools/issues/49) for details.

        EXAMPLE::

            APS = apstools.devices.ApsMachineParametersDevice(name="APS")

            if APS.inUserOperations:
                suspend_APS_current = bluesky.suspenders.SuspendFloor(APS.current, 2, resume_thresh=10)
                RE.install_suspender(suspend_APS_current)
            else:
                # use pseudo shutter controls and no current suspenders
                pass

        """
        # fmt: off
        return self.machine_status.get() in (
            1, "USER OPERATIONS",
            2, "Bm Ln Studies",
        )
        # fmt: on

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
