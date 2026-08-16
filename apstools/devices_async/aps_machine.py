import logging
from typing import Annotated as A

from ophyd_async.core import SignalR, StandardReadable
from ophyd_async.core import StandardReadableFormat as Format
from ophyd_async.core import StrictEnum, SubsetEnum
from ophyd_async.epics.core import EpicsDevice, PvSuffix, epics_signal_r

log = logging.getLogger(__name__)


class ApsMachine(EpicsDevice, StandardReadable):

    _ophyd_labels_ = {"synchrotrons"}

    class MachineStatus(SubsetEnum):
        UNKNOWN = "State Unknown"
        USER_OPERATIONS = "USER OPERATIONS"
        SUPPLEMENTAL_TIME = "SUPLEMENTAL TIME"
        ASD_STUDIES = "ASD Studies"
        NO_BEAM = "NO BEAM"
        MAINTENANCE = "MAINTENANCE"

    class OperatingMode(StrictEnum):
        STATE_UNKNOWN = "State Unknown"
        NO_BEAM = "NO BEAM"
        INJECTING = "Injecting"
        STORED_BEAM = "Stored Beam"
        DELIVERED_BEAM = "Delivered Beam"
        MAINTENANCE = "MAINTENANCE"

    current: A[SignalR[float], PvSuffix("S-DCCT:CurrentM"), Format.CHILD]
    operators: A[SignalR[str], PvSuffix("OPS:message1"), Format.CONFIG_SIGNAL]
    floor_coordinator: A[SignalR[str], PvSuffix("OPS:message2"), Format.CONFIG_SIGNAL]
    fill_pattern: A[SignalR[str], PvSuffix("OPS:message3"), Format.CONFIG_SIGNAL]
    last_problem_message: A[
        SignalR[str], PvSuffix("OPS:message4"), Format.CONFIG_SIGNAL
    ]
    last_trip_message: A[SignalR[str], PvSuffix("OPS:message5"), Format.CONFIG_SIGNAL]
    # messages 6-8: meaning?
    message6: A[SignalR[str], PvSuffix("OPS:message6"), Format.CONFIG_SIGNAL]
    message7: A[SignalR[str], PvSuffix("OPS:message7"), Format.CONFIG_SIGNAL]
    message8: A[SignalR[str], PvSuffix("OPS:message8"), Format.CONFIG_SIGNAL]
    machine_status: A[
        SignalR[MachineStatus], PvSuffix("S:DesiredMode"), Format.CONFIG_SIGNAL
    ]
    operating_mode: A[
        SignalR[OperatingMode], PvSuffix("S:ActualMode"), Format.CONFIG_SIGNAL
    ]
    shutter_status: A[
        SignalR[bool], PvSuffix("XFD:ShutterPermit"), Format.CONFIG_SIGNAL
    ]
    shutters_open: A[SignalR[int], PvSuffix("NoOfShuttersOpenA"), Format.CONFIG_SIGNAL]
    fill_number: A[SignalR[int], PvSuffix("S:FillNumber"), Format.CONFIG_SIGNAL]
    orbit_correction: A[
        SignalR[float], PvSuffix("S:OrbitCorrection:CC"), Format.CONFIG_SIGNAL
    ]


# -----------------------------------------------------------------------------
# :author:    Mark Wolfman
# :email:     wolfman@anl.gov
# :copyright: Copyright © 2023, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
