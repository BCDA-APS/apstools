#!/usr/bin/env python

"""
record a snapshot of some PVs using Bluesky, ophyd, and databroker
"""


import argparse
from collections import OrderedDict
import sys
import time

from APS_BlueSky_tools import utils as APS_utils
from APS_BlueSky_tools import plans as APS_plans
from APS_BlueSky_tools import callbacks as APS_callbacks


BROKER_CONFIG = "mongodb_config"
# TODO: caller may want to provide more metadata


def get_args():
    """
    get command line arguments
    """
    #from .__init__ import __version__
    doc = __doc__.strip()
    parser = argparse.ArgumentParser(description=doc)

    parser.add_argument('EPICS_PV', action='store', nargs='+',
                        help="EPICS PV name", default="")

    # optional arguments
    parser.add_argument('-b', action='store', dest='broker_config',
                        help="YAML configuration for databroker", 
                        default="mongodb_config")

    help = """
    additional metadata, enclose in quotes,
    such as -m "purpose=just tuned, situation=routine"
    """
    parser.add_argument('-m', action='store', dest='metadata',
                        help=help, 
                        default="")

    return parser.parse_args()


def parse_metadata(args):
    md = OrderedDict()
    for metadata in args.metadata.split(","):
        parts = metadata.strip().split("=")
        if len(parts) == 2:
            md[parts[0].strip()] = parts[1].strip()
        else:
            msg = f"incorrect metadata specification {metadata}"
            msg += ", must specify key = value [, key2 = value2 ]"
            raise ValueError(msg)
    return md


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

    args = get_args()
    
    md = OrderedDict(purpose="python code development and testing")
    md.update(parse_metadata(args))

    obj_dict = APS_utils.connect_pvlist(args.EPICS_PV, wait=False)
    time.sleep(2)   # FIXME: allow time to connect
    
    db = Broker.named(args.broker_config)
    RE = RunEngine({})
    RE.subscribe(db.insert)

    uuid_list = RE(APS_plans.snapshot(obj_dict.values(), md=md))
    
    snap = list(db(uuid_list[0]))[0]
    APS_callbacks.SnapshotReport().print_report(snap)


if __name__ == "__main__":
    snapshot_cli()
