"""
Callbacks that might be useful at the APS using Bluesky

.. autosummary::

   ~document_contents_callback
   ~DocumentCollectorCallback
   ~SnapshotReport

FILE WRITER CALLBACK

see :class:`SpecWriterCallback()`

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

import datetime
import logging
import pyRestTable
from bluesky.callbacks.core import CallbackBase


logger = logging.getLogger(__name__).addHandler(logging.NullHandler())


def document_contents_callback(key, doc):
    """
    prints document contents -- use for diagnosing a document stream
    """
    print(key)
    for k, v in doc.items():
        print(f"\t{k}\t{v}")


class DocumentCollectorCallback(object):
    """
    Bluesky callback to collect *all* documents from most-recent plan

    .. index:: Bluesky Callback; DocumentCollectorCallback

    Will reset when it receives a *start* document.

    EXAMPLE::

        from apstools.callbacks import DocumentCollectorCallback
        doc_collector = DocumentCollectorCallback()
        RE.subscribe(doc_collector.receiver)
        ...
        RE(some_plan())
        print(doc_collector.uids)
        print(doc_collector.documents["stop"])

    """

    data_event_names = (
        "descriptor event resource datum bulk_events".split()
    )

    def __init__(self):
        self.documents = {}  # key: name, value: document
        self.uids = []  # chronological list of UIDs as-received

    def receiver(self, key, document):
        """keep all documents from recent plan in memory"""
        uid = document.get("uid") or document.get("datum_id")
        if uid is None:
            raise KeyError("No uid in '{}' document".format(key))
        self.uids.append(uid)
        logger = logging.getLogger(__name__)
        logger.debug("%s document  uid=%s", key, str(uid))
        if key == "start":
            self.documents = {key: document}
        elif key in self.data_event_names:
            if key not in self.documents:
                self.documents[key] = []
            self.documents[key].append(document)
        elif key == "stop":
            self.documents[key] = document
            print("exit status:", document["exit_status"])
            for item in self.data_event_names:
                if item in self.documents:
                    print(f"# {len(self.documents[item])}(s):")
        else:
            txt = "custom_callback encountered: %s\n%s"
            logger.warning(txt, key, document)
            if key not in self.documents:
                self.documents[key] = []
            self.documents[key].append(document)
        return


class SnapshotReport(CallbackBase):
    """
    show the data from a ``apstools.plans.snapshot()``

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
                    .isoformat()
                    .replace("T", " ")
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
