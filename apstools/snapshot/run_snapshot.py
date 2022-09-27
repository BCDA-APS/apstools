#!/usr/bin/env python

"""
let the developer test the snapshot tool in the source directory
"""

import sys

sys.path.insert(0, "..")

import apstools.snapshot

if __name__ == "__main__":
    apstools.snapshot.snapshot_cli()

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
