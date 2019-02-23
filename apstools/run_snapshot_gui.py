#!/usr/bin/env python

"""
let the developer test the snapshot tool in the source directory
"""

import sys
sys.path.insert(0, "..")
 
import apstools.snapshot

config = "mongodb_config"
# config = "mongodb_localhost"
# config = "mongodb_poof"

if __name__ == "__main__":
    apstools.snapshot.snapshot_gui(config)
