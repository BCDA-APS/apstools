#!/usr/bin/env python

"""
demonstrate a BlueSky callback that writes SPEC data files
"""


import datetime
from databroker import Broker
from filewriters import SpecWriterCallback, _rebuild_scan_command


def specfile_example(headers, path=None):
    specwriter = SpecWriterCallback(path, auto_write=False)
    if not isinstance(headers, list):
        headers = [headers]
    for h in headers:
        for key, doc in h.db.get_documents(h):
            specwriter.receiver(key, doc)
        lines = specwriter.prepare_file_contents()
        if lines is not None:
            print("\n".join(lines))
        print("#"*60)


def plan_catalog(db):
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
    print(t)
    print("Found {} plans (start documents)".format(len(t.rows)))



if __name__ == "__main__":
    # load config from ~/.config/databroker/mongodb_config.yml
    #db = Broker.named("mongodb_config")
    mongodb_config = {
        'description': 'heavyweight shared database',
        'metadatastore': {
            'module': 'databroker.headersource.mongo',
            'class': 'MDS',
            'config': {
                'host': 'localhost',
                'port': 27017,
                'database': 'prj-metadatastore-testing',
                'timezone': 'US/Central'
            }
        },
        'assets': {
            'module': 'databroker.assets.mongo',
            'class': 'Registry',
            'config': {
                'host': 'localhost',
                'port': 27017,
                'database': 'prj-metadatastore-testing'
            }
        }
    }
    db = Broker.from_config(mongodb_config)

    plan_catalog(db)
    # specfile_example(db[-1])
    # specfile_example(db[-1:])
    # specfile_example(db["1d2a3890"])
    # specfile_example(db["15d12d"])
    # specfile_example(db["b7f84d0c"])
    # specfile_example(db["83c440c2"])
    # specfile_example(db["ebdcbfb8"])
    # specfile_example(db[-10:-5])
    # specfile_example(db[-80])
    # specfile_example(db[-10000:][-25:])
    # specfile_example(db["82df580d"])
