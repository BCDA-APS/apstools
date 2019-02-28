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


def plan_catalog(db):
    """
    make a table of all scans known in the databroker
    
    Example::
    
        from apstools.examples import plan_catalog
        plan_catalog(db)
    
    """
    import pyRestTable
    t = pyRestTable.Table()
    t.labels = "date/time short_uid id plan args".split()
    for h in db.hs.find_run_starts():
        row = []
        dt = datetime.datetime.fromtimestamp(h["time"])
        row.append(str(dt).split(".")[0])
        row.append(h['uid'][:8])
        command = _rebuild_scan_command(h)
        scan_id = command.split()[0]
        command = command[len(scan_id):].strip()
        plan = command.split("(")[0]
        args = command[len(plan)+1:].rstrip(")")
        row.append(scan_id)
        row.append(plan)
        row.append(args)
        t.addRow(row)
    t.rows = t.rows[::-1]   # reverse the list
    return t


def main():
    """
    summary list of all scans in the databroker

    ``apstools_plan_catalog`` command-line application
    
    This can be unwieldy if there are many scans in the databroker.
    Consider it as a demo program rather than for general, long-term use.
    """
    from databroker import Broker
    # load config from ~/.config/databroker/mongodb_config.yml
    db = Broker.named("mongodb_config")
    table = plan_catalog(db)
    print(table)
    print("Found {} plans (start documents)".format(len(table.rows)))


if __name__ == "__main__":
    main()

    # load config from ~/.config/databroker/mongodb_config.yml
    # db = Broker.named("mongodb_config")

    # plan_catalog(db)
    # specfile_example(db[-1])
    # specfile_example(db[-5:][::-1])
    # specfile_example(db["1d2a3890"])
    # specfile_example(db["15d12d"])
    # specfile_example(db[-10:-5])
    # specfile_example(db[-80])
    # specfile_example(db[-10000:][-25:])
