

"""
a BlueSky callback that writes SPEC data files
"""


import os
import sys
from databroker import Broker
from filewriters import SpecWriterCallback

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



def example(db, db_key=None, path=None):
    specwriter = SpecWriterCallback(path, auto_write=False)
    db_key = db_key or -1
    h = db[db_key]
    for key, doc in db.get_documents(db[db_key]):
        specwriter.receiver(key, doc)
    lines = specwriter.prepare_file_contents()
    print("\n".join(lines))


def scan_catalog(db):
    import pyRestTable
    n = len(db[-10000:])
    t = pyRestTable.Table()
    t.labels = "index uid scan_id plan_name plan_args".split()
    for i in range(n):
        _i = i - n
        h = db[_i]['start']
        row = [_i]
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
        

if __name__ == "__main__":
    # scan_catalog(db)
    # #example(db, db_key="15d12d")
    example(db)
    # example(db, db_key="b7f84d0c")
    # example(db, db_key="83c440c2")
    # example(db, db_key="ebdcbfb8")
