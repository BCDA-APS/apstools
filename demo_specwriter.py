#!/usr/bin/env python

"""
demonstrate a BlueSky callback that writes SPEC data files
"""


import datetime
from databroker import Broker
from filewriters import SpecWriterCallback


def example(headers, path=None):
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
    n = len(db[-10000:])
    t = pyRestTable.Table()
    t.labels = "# date/time short_uid scan_id plan_name plan_args".split()
    for i in range(n):
        _i = i - n
        h = db[_i]['start']
        row = [_i]
        dt = datetime.datetime.fromtimestamp(h["time"])
        row.append(str(dt).split(".")[0])
        row.append(h['uid'][:8])
        row.append(h['scan_id'])
        row.append(h['plan_name'])
        s = []
        for _k, _v in h['plan_args'].items():
            if _k == "detectors":
                _v = h[_k]
            elif _k.startswith("motor"):
                _v = h["motors"]
            s.append("{}={}".format(_k, _v))
        row.append(", ".join(s))
        t.addRow(row)
    print(t)


def setup_broker():
    # load config from ~/.config/databroker/mongodb_config.yml
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
    return db

if __name__ == "__main__":
    db = setup_broker()

    plan_catalog(db)
    # example(db[-1])
    # example(db[-1:])
    # example(db["1d2a3890"])
    # example(db["15d12d"])
    # example(db["b7f84d0c"])
    # example(db["83c440c2"])
    # example(db["ebdcbfb8"])
    # example(db[-10:-5])
    # example(db[-100])
    # example(db[-10000:][-25:])
