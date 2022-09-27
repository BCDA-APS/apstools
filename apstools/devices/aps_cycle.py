"""
APS cycles
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~ApsCycleDM
"""

import datetime
import json
from ophyd.sim import SynSignalRO
import pathlib
import time
import yaml


_PATH = pathlib.Path(__file__).parent
YAML_CYCLE_FILE = (_PATH / "aps_cycle_info.yml")


class _ApsCycleDB:
    """
    Python representation of the APS run cycle schedule table.
    """

    def __init__(self):
        self.db = self._read_cycle_data()

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
        Read the list of APS run cycles from a local file.

        The file is formatted in YAML after reformatting content received from
        the APS Data Management package (*aps-dm-api*).  The YAML format is
        easily updated and human-readable.
        """
        _cycles_yml = YAML_CYCLE_FILE.open().read()
        _cycles = yaml.load(_cycles_yml, Loader=yaml.BaseLoader)

        def iso2ts(isodatetime):
            return datetime.datetime.timestamp(
                datetime.datetime.fromisoformat(isodatetime)
            )

        db = {
            run_name: dict(
                start=iso2ts(span["begin"]), end=iso2ts(span["end"])
            )
            for run_name, span in _cycles.items()
        }
        return db

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
            cycle_data = runs.replace("'", '"')
            cycles = json.loads(cycle_data)

            def sorter(line):
                return line["name"]

            db = {
                line["name"]: {
                    "begin": line["startTime"],
                    "end": line["endTime"],
                }
                for line in sorted(cycles, key=sorter)
            }
            with YAML_CYCLE_FILE.open("w") as f:
                f.write(yaml.dump(db))

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

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
