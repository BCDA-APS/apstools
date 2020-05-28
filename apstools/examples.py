#!/usr/bin/env python

"""
demonstrate BlueSky callbacks

.. autosummary::
   
   ~plan_catalog
   ~specfile_example

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


import databroker
import datetime
from .filewriters import SpecWriterCallback, _rebuild_scan_command
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
DEMO_SPEC_FILE = "test_specdata.txt"


def specfile_example(headers, filename=DEMO_SPEC_FILE):
    """write one or more headers (scans) to a SPEC data file"""
    specwriter = SpecWriterCallback(filename=filename, auto_write=True)
    if not isinstance(headers, (list, databroker._core.Results)):
        headers = [headers]
    for h in headers:
        for key, doc in h.db.get_documents(h):
            specwriter.receiver(key, doc)
        lines = specwriter.prepare_scan_contents()
        if lines is not None:
            logger.info("\n".join(lines))
        logger.info("#"*60)
    logger.info("Look at SPEC data file: "+specwriter.spec_filename)


if __name__ == "__main__":

    # load config from ~/.config/databroker/mongodb_config.yml
    # db = Broker.named("mongodb_config")

    # specfile_example(db[-1])
    # specfile_example(db[-5:][::-1])
    # specfile_example(db["1d2a3890"])
    # specfile_example(db["15d12d"])
    # specfile_example(db[-10:-5])
    # specfile_example(db[-80])
    # specfile_example(db[-10000:][-25:])
