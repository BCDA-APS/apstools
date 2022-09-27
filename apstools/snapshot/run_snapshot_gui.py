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
    "mongodb_localhost",
]

if __name__ == "__main__":
    ext = ".yml"
    for config in developer_config_candidates:
        print("Trying mongodb configuration: " + config + ext)
        try:
            apstools.snapshot.snapshot_gui(config)
            break
        except FileNotFoundError as exc:
            print("Mongodb configuration file not found: " + config + ext)
            print(exc)
        except ServerSelectionTimeoutError:
            print(
                "Connection timeout with mongodb server: " + config + ext
            )

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
