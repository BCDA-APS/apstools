"""
APS cycles
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~ApsCycleComputedRO
   ~ApsCycleDM
"""

from datetime import datetime
from ophyd.sim import SynSignalRO


class ApsCycleDM(SynSignalRO):
    """
    Get the APS cycle name from the APS Data Management system.

    .. index:: Ophyd Signal; ApsCycleDM

    This signal is read-only.
    """

    _cycle_ends = "1980"  # force a read from DM on first get()
    _cycle_name = "unknown"

    def get(self):
        if datetime.now().isoformat(sep=" ") >= self._cycle_ends:
            from ..beamtime.apsbss import api_bss

            # only update from data management after the end of the run
            cycle = api_bss.getCurrentRun()
            self._cycle_name = cycle["name"]
            self._cycle_ends = cycle["endTime"]
        return self._cycle_name


class ApsCycleComputedRO(SynSignalRO):
    """
    Compute the APS cycle name based on the calendar and the usual practice.

    .. index:: Ophyd Signal; ApsCycleComputedRO

    Absent any facility PV that provides the name of the current operating
    cycle, this can be approximated by python computation (as long as the
    present scheduling pattern is maintained)

    This signal is read-only.

    NOTE: There is info provided by the APS proposal & ESAF systems.  See
    :class:`~ApsCycleDM`.
    """

    def get(self):
        dt = datetime.now()
        aps_cycle = f"{dt.year}-{int((dt.month-0.1)/4) + 1}"
        return aps_cycle
