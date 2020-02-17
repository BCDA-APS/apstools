
"""
prints snapshot contents

.. autosummary::
   
   ~SnapshotReport
"""

__all__ = ["SnapshotReport",]


import logging
logger = logging.getLogger(__name__)

import datetime
import pyRestTable

from .doc_contents import document_contents_callback


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

        # The only way we have a stream that is not "primary"
        # is when the snapshot has been made from python code.
        # The command line tool will not create additional streams.
        if doc["name"] == "primary":
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
        document_contents_callback(t, doc)
    
    def print_report(self, header):
        """
        simplify the job of writing our custom data table
        
        method: play the entire document stream through this callback
        """
        print()
        print("="*40)
        print("snapshot:", header.start["iso8601"])
        print("="*40)
        document_contents_callback("", header.start)
        print()
        for key, doc in header.documents():
            self(key, doc)        
        print()
