#!/usr/bin/env python

"""
let the developer test the snapshot tool in the source directory
"""

#-----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2019, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
#-----------------------------------------------------------------------------

import sys
sys.path.insert(0, "..")

import apstools.snapshot

if __name__ == "__main__":
    apstools.snapshot.snapshot_cli()
