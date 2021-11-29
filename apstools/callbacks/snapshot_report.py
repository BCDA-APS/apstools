"""
Snapshot Report
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~SnapshotReport
"""

import datetime
import pyRestTable
from bluesky.callbacks.core import CallbackBase


class SnapshotReport(CallbackBase):
    """
    Show the data from a ``apstools.plans.snapshot()``.

    Find most recent snapshot between certain dates::

        headers = db(plan_name="snapshot", since="2018-12-15", until="2018-12-21")
        h = list(headers)[0]        # pick the first one, it's the most recent
        apstools.callbacks.SnapshotReport().print_report(h)

    Use as callback to a snapshot plan::

        RE(
            apstools.plans.snapshot(ophyd_objects_list),
            apstools.callbacks.SnapshotReport()
        )

    """

    xref = None

    def start(self, doc):
        if doc.get("plan_name", "nope") == "snapshot":
            # key=source, value=dict(value, iso8601 timestamp)
            self.xref = {}
        else:
            self.xref = None

    def descriptor(self, doc):
        """
        special case:
           the data is both in the descriptor AND the event docs
           due to the way our plan created it
        """
        if self.xref is None:  # not from a snapshot plan
            return

        # The only way we have a stream that is not "primary"
        # is when the snapshot has been made from python code.
        # The command line tool will not create additional streams.
        if doc["name"] == "primary":
            for k, v in doc["configuration"].items():
                ts = v["timestamps"][k]
                dt = (
                    datetime.datetime.fromtimestamp(ts)
                    .isoformat(sep=" ")
                )
                pvname = v["data_keys"][k]["source"]
                value = v["data"][k]
                self.xref[pvname] = dict(value=value, timestamp=dt)

    def stop(self, doc):
        if self.xref is None:  # not from a snapshot plan
            return

        t = pyRestTable.Table()
        t.addLabel("timestamp")
        t.addLabel("source")
        t.addLabel("name")
        t.addLabel("value")
        for k, v in sorted(self.xref.items()):
            p = k.find(":")
            # fmt: off
            t.addRow((v["timestamp"], k[:p], k[p + 1:], v["value"]))
            # fmt: on
        print(t)
        for k, v in sorted(doc.items()):
            print(f"{k}: {v}")

    def print_report(self, header):
        """
        simplify the job of writing our custom data table

        method: play the entire document stream through this callback
        """
        print()
        print("=" * 40)
        print("snapshot:", header.start["iso8601"])
        print("=" * 40)
        print()
        for k, v in sorted(header.start.items()):
            print(f"{k}: {v}")
        print()
        for key, doc in header.documents():
            self(key, doc)
        print()

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
