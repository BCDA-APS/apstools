
"""
Callbacks that might be useful at the APS using BlueSky

.. autosummary::
   
   ~document_contents_callback
   ~DocumentCollectorCallback
   ~SnapshotReport

FILE WRITER CALLBACK

see :class:`SpecWriterCallback()`

"""

# Copyright (c) 2017-2018, UChicago Argonne, LLC.  See LICENSE file.

import datetime
import logging
import pyRestTable
from bluesky.callbacks.core import CallbackBase


logger = logging.getLogger(__name__).addHandler(logging.NullHandler())


def document_contents_callback(key, doc):
    """
    prints document contents
    """
    print(key)
    for k, v in doc.items():
        print(f"\t{k}\t{v}")


class DocumentCollectorCallback(object):
    """
    BlueSky callback to collect *all* documents from most-recent plan
    
    Will reset when it receives a *start* document.
    
    EXAMPLE::
    
        from APS_BlueSky_tools.callbacks import DocumentCollector
        doc_collector = DocumentCollectorCallback()
        RE.subscribe(doc_collector.receiver)
        ...
        RE(some_plan())
        print(doc_collector.uids)
        print(doc_collector.documents["stop"])
    
    """
    data_event_names = "descriptor event resource datum bulk_events".split()
    
    def __init__(self):
        self.documents = {}     # key: name, value: document
        self.uids = []          # chronological list of UIDs as-received

    def receiver(self, key, document):
        """keep all documents from recent plan in memory"""
        uid = document.get("uid") or document.get("datum_id")
        if "uid" is None:
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
                    print(
                        "# {}(s):".format(item), 
                        len(self.documents[item])
                    )
        else:
            txt = "custom_callback encountered: %s\n%s"
            logger.warning(txt, key, document)
            if key not in self.documents:
                self.documents[key] = []
            self.documents[key].append(document)
        return


class SnapshotReport(CallbackBase):
    """
    show the data from a ``APS_BlueSky_Tools.plans.snapshot()``
    """
    
    xref = None
    
    def start(self, doc):
        if doc.get("plan_name", "nope") == "snapshot":
            self.xref = {}    # key=source, value=dict(value, iso8601 timestamp)
        else:
            self.xref = None
    
    def descriptor(self, doc):
        """
        special case:  
           the data is both in the descriptor AND the event docs
           due to the way our plan created it
        """
        if self.xref is None:       # not from a snapshot plan
            return

        for k, v in doc["configuration"].items():
            ts = v["timestamps"][k]
            dt = datetime.datetime.fromtimestamp(ts).isoformat().replace("T", " ")
            pvname = v["data_keys"][k]["source"]
            value = v["data"][k]
            self.xref[pvname] = dict(value=value, timestamp=dt)
    
    def stop(self, doc):
        if self.xref is None:       # not from a snapshot plan
            return

        t = pyRestTable.Table()
        t.addLabel("timestamp")
        t.addLabel("source")
        t.addLabel("name")
        t.addLabel("value")
        for k, v in sorted(self.xref.items()):
            p = k.find(":")
            t.addRow((v["timestamp"], k[:p], k[p+1:], v["value"]))
        print(t)
        for k, v in sorted(doc.items()):
            print(f"{k}: {v}")
    
    def print_report(self, header):
        """
        simplify the job of writing our custom data table
        
        method: play the entire document stream through this callback
        """
        if self.xref is None:       # not from a snapshot plan
            return

        print()
        print("="*40)
        print("snapshot:", header.start["iso8601"])
        print("="*40)
        print()
        for k, v in sorted(header.start.items()):
            print(f"{k}: {v}")
        print()
        for key, doc in header.documents():
            self(key, doc)        
        print()
