#!/usr/bin/env python

"""
record a snapshot of some PVs using Bluesky, ophyd, and databroker
"""


import sys
import time
from APS_BlueSky_tools import utils as APS_utils
from APS_BlueSky_tools import plans as APS_plans
from APS_BlueSky_tools import callbacks as APS_callbacks


# TODO: caller may want to change this
BROKER_CONFIG = "mongodb_config"
# TODO: caller may want to provide more metadata


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

    obj_dict = APS_utils.connect_pvlist(pvlist, wait=False)
    time.sleep(2)   # FIXME: allow time to connect
    
    RE = RunEngine({})
    # RE(
    #     APS_plans.snapshot(obj_dict.values()), 
    #     APS_callbacks.document_contents_callback)
    
    db = Broker.named(BROKER_CONFIG)
    RE.subscribe(db.insert)
    uuid_list = RE(
        APS_plans.snapshot(
            obj_dict.values(), 
            md=dict(purpose="python code development and testing")))
    
    snap = list(db(uuid_list[0]))[0]
    #print(h.start)
    #print(h.table())
    APS_callbacks.SnapshotReport().print_report(snap)


if __name__ == "__main__":
    snapshot_cli()
