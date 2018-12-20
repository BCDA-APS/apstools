#!/usr/bin/env python

"""
record a snapshot of some PVs using Bluesky, ophyd, and databroker
"""


from collections import OrderedDict
import datetime
import os
import pyRestTable
import sys
import time

import bluesky
import databroker
import epics
import ophyd
import APS_BlueSky_tools


from ophyd import EpicsSignal, Signal
from bluesky import (
    plans as bp, 
    plan_patterns as bpp, 
    plan_stubs as bps, 
    plan_tools as bpt)
from bluesky.callbacks.core import CallbackBase


def connect_pvlist(pvlist, wait=True, timeout=2, poll_interval=0.2):
    obj_dict = OrderedDict()
    for item in pvlist:
        if len(item.strip()) == 0:
            continue
        pvname = item.strip()
        oname = "signal_{}".format(len(obj_dict))
        obj = EpicsSignal(pvname, name=oname)
        obj_dict[oname] = obj

    if wait:
        times_up = time.time() + min(0, timeout)
        poll_interval = min(0.01, poll_interval)
        waiting = True
        while waiting and time.time() < times_up:
            time.sleep(poll_interval)
            waiting = False in [o.connected for o in obj_dict.values()]
        if waiting:
            n = OrderedDict()
            for k, v in obj_dict.items():
                if v.connected:
                    n[k] = v
                else:
                    print(f"Could not connect {v.pvname}")
            if len(n) == 0:
                raise RuntimeError("Could not connect any PVs in the list")
            obj_dict = n

    return obj_dict


def snapshot(obj_list, stream="primary", md=None):
    """
    bluesky plan: record current value of list of ophyd signals
    """
    validated_objects = []
    for obj in obj_list:
        # TODO: consider supporting Device objects
        if isinstance(obj, (Signal, EpicsSignal)):
            validated_objects.append(obj)
        else:
            raise RuntimeWarning(f"ignoring object: {obj}")
        
        if len(validated_objects) == 0:
            raise ValueError("No signals to log.")

    # we want this metadata to appear
    _md = dict(
        plan_name = "snapshot",
        plan_description = "archive snapshot of ophyd Signals (usually EPICS PVs)",
        iso8601 = str(datetime.datetime.now()),     # human-readable
        hints = {},
        software_versions = dict(
            PYTHON = sys.version,
            PYEPICS = epics.__version__,
            BLUESKY = bluesky.__version__,
            OPHYD = ophyd.__version__,
            DATABROKER = databroker.__version__,
            APS_BLUESKY_TOOLS = APS_BlueSky_tools.__version__,),
        )
    # caller may have given us additional metadata
    _md.update(md or {})

    def _snap(md=None):
        yield from bps.open_run(md)
        yield from bps.create(name=stream)
        for obj in validated_objects:
            # passive observation: DO NOT TRIGGER, only read
            yield from bps.read(obj)
        yield from bps.save()
        yield from bps.close_run()

    return (yield from _snap(md=_md))


def callback(key, doc):
    print(key)
    for k, v in doc.items():
        print(f"\t{k}\t{v}")


class SnapshotReport(CallbackBase):
    
    xref = {}    # key=PVname, value=dict(value, iso8601 timestamp)
    
    def descriptor(self, doc):
        """
        special case:  
           the data is both in the descriptor AND the event docs
           due to the way our plan created it
        """
        self.xref = {}
        for k, v in doc["configuration"].items():
            ts = v["timestamps"][k]
            dt = datetime.datetime.fromtimestamp(ts).isoformat().replace("T", " ")
            pvname = v["data_keys"][k]["source"]
            value = v["data"][k]
            self.xref[pvname] = dict(value=value, timestamp=dt)
    
    def stop(self, doc):
        t = pyRestTable.Table()
        t.addLabel("source")
        t.addLabel("name")
        t.addLabel("value")
        t.addLabel("timestamp")
        for k, v in sorted(self.xref.items()):
            p = k.find(":")
            t.addRow((k[:p], k[p+1:], v["value"], v["timestamp"]))
        print(t)
    
    def print_report(self, header):
        """
        simplify the job of writing our custom data table
        
        method: play the entire document stream through this callback
        """
        print()
        print("="*40)
        print("snapshot:", header.start["iso8601"])
        print("="*40)
        print()
        for k, v in sorted(header.start.items()):
            #if k not in plan_keys:
                print(f"{k}: {v}")
        print()
        for key, doc in header.documents():
            self(key, doc)        
        print()


def snapshot_cli():
    """
    given a list of PVs on the command line, snapshot and print report
    
    EXAMPLES::
    
        snapshot.py pv1 [more pvs ...]
        snapshot.py `cat pvlist.txt`

    Note that these are equivalent::

        snapshot.py rpi5bf5:0:humidity rpi5bf5:0:temperature
        snapshot.py rpi5bf5:0:{humidity,temperature}

    """
    from databroker import Broker
    from bluesky import RunEngine

    pvlist = sys.argv[1:]

    obj_dict = connect_pvlist(pvlist, wait=False)
    time.sleep(2)   # FIXME: allow time to connect
    
    RE = RunEngine({})
    RE(snapshot(obj_dict.values()))
    
    db = Broker.named("mongodb_config")
    RE.subscribe(db.insert)
    RE(
        snapshot(
            obj_dict.values(), 
            md=dict(purpose="python code development and testing")))
    
    h = db[-1]
    #print(h.start)
    #print(h.table())
    SnapshotReport().print_report(h)


if __name__ == "__main__":
    snapshot_cli()
