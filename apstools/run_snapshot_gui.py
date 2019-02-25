#!/usr/bin/env python

"""
let the developer test the snapshot tool in the source directory
"""

import sys
sys.path.insert(0, "..")
 
import apstools.snapshot
from pymongo.errors import ServerSelectionTimeoutError

developer_config_candidates = [
    "mongodb_config",
    "mongodb_poof",
    "mongodb_ookhd",
    ]

if __name__ == "__main__":
    ext =  ".yml"
    for config in developer_config_candidates:
        print("Trying mongodb configuration: " + config + ext)
        try:
            apstools.snapshot.snapshot_gui(config)
            break
        except FileNotFoundError as exc:
            print("Mongodb configuration file not found: " + config + ext)
            print(exc)
        except ServerSelectionTimeoutError:
            print("Timeout when cennecting with mongodb server: " + config + ext)
