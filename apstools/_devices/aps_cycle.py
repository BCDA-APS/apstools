"""
APS cycles
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~ApsCycleComputedRO
   ~ApsCycleDM
"""

import datetime
from ophyd.sim import SynSignalRO
import json
import os
import time
import warnings


LOCAL_FILE = os.path.join(os.path.dirname(__file__), "aps_cycle_info.txt")


class _ApsCycleDB:
    """
    Python representation of the APS run cycle schedule table.
    """

    def __init__(self):
        self.source = None  # source of cycle information
        if not os.path.exists(LOCAL_FILE):
            self._write_cycle_data()

        # transform raw cycle data into JSON by replacing all ' with "
        _cycles = json.loads(self._read_cycle_data().replace("'", '"'))
        self.db = {
            line["name"]: {
                "start": datetime.datetime.timestamp(
                    datetime.datetime.fromisoformat(line["startTime"])
                ),
                "end": datetime.datetime.timestamp(
                    datetime.datetime.fromisoformat(line["endTime"])
                ),
            }
            for line in _cycles
        }

    def get_cycle_name(self, ts=None):
        """
        Get the name of the current APS run cycle.

        By default, the name of the current run cycle (based on the
        current timestamp) will be returned.

        PARAMETERS

        ts float:
            Absolute time stamp (such as from ``time.time()``).
            Default: current time stamp.

        RETURNS

        Returns cycle name (str) or ``None`` if timestamp is not in data table.
        """
        ts = ts or time.time()
        for cycle, span in self.db.items():
            if span["start"] <= ts < span["end"]:
                return cycle
        return None  # not found

    def _read_cycle_data(self):
        """
        Read the list of APS run cycles from *aps-dm-api* or a local file.

        The file is formatted exactly as received from the
        APS Data Management package (*aps-dm-api*).  This allows
        automatic updates as needed.
        """
        table = self._bss_list_runs
        if table is None:
            table = open(LOCAL_FILE, "r").read()
            self.source = "file"
        else:
            self.source = "aps-dm-api"
        return table

    def _write_cycle_data(self):
        """
        Write the list of APS run cycles to a local file.

        The file is formatted exactly as received from the
        APS Data Management package (*aps-dm-api*).  This allows
        automatic updates as needed.

        To update the LOCAL_FILE, run this code (on a workstation at the APS)::

            from apstools._devices.aps_cycle import cycle_db
            cycle_db._write_cycle_data()
        """
        runs = self._bss_list_runs
        if runs is not None:
            open(LOCAL_FILE, "w").write(self._bss_list_runs)

    @property
    def _bss_list_runs(self):
        try:
            import apsbss

            return str(apsbss.api_bss.listRuns())
        except ModuleNotFoundError:
            return None


cycle_db = _ApsCycleDB()


class ApsCycleDM(SynSignalRO):
    """
    Get the APS cycle name from the APS Data Management system or a local file.

    .. index:: Ophyd Signal; ApsCycleDM

    This signal is read-only.
    """

    _cycle_ends = "1980"  # force a read from DM on first get()
    _cycle_name = "unknown"

    def get(self):
        self._cycle_name = cycle_db.get_cycle_name()
        if datetime.datetime.now().isoformat(sep=" ") >= self._cycle_ends:
            self._cycle_ends = datetime.datetime.fromtimestamp(
                cycle_db.db[self._cycle_name]["end"]
            ).isoformat(sep=" ")
        return self._cycle_name


class ApsCycleComputedRO(SynSignalRO):
    """
    DEPRECATED (1.5.4): Use newer ``ApsCycleDM`` instead.

    Compute the APS cycle name based on the calendar and the usual practice.

    .. index:: Ophyd Signal; ApsCycleComputedRO

    Absent any facility PV that provides the name of the current operating
    cycle, this can be approximated by python computation (as long as the
    present scheduling pattern is maintained)

    This signal is read-only.

    NOTE: There is info provided by the APS proposal & ESAF systems.  See
    :class:`~ApsCycleDM`.
    """

    def __init__(self, *args, **kwargs):
        warnings.warn(
            "DEPRECATED: ApsCycleComputedRO() will be removed"
            " in a future release.  Instead, use newer ``ApsCycleDM``.",
            DeprecationWarning,
        )
        super().__init__(*args, **kwargs)

    def get(self):
        dt = datetime.datetime.now()
        aps_cycle = f"{dt.year}-{int((dt.month-0.1)/4) + 1}"
        return aps_cycle
