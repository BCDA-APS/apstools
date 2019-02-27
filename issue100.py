
"""
work on issue 100
"""

from databroker import Broker
from apstools import filewriters as APS_filewriters
import os
import datetime
import pyRestTable

uids = """
    48279fc0 034a9061 a7aca928 9c359710 1f4b7f4f 704d8433 
    3ffb89e0 fa05f8f8 0b485f0c 475b3439 969544d4 33446187
    c6132881 45314578 70be8a1e f1eeb72a f834ea64 037d1f5d
    d8b1d269 6056675d 163898da 281cb584 c7a1dd12
    """.split()
db = Broker.named("mongodb_config")

fname = "spec_issue100.dat"
if os.path.exists(fname):
    os.remove(fname)
specwriter = APS_filewriters.SpecWriterCallback()
specwriter.newfile(fname)
for uid in uids:
    for key, doc in db[uid].documents():
        specwriter.receiver(key, doc)
print("Look at SPEC data file: "+specwriter.spec_filename)

tbl = pyRestTable.Table()
tbl.labels = "# timestamp scan_id uid plan_name".split()
for i, h in enumerate(db()):
    st = h.start
    uid = st["uid"][:8]
    scann = st["scan_id"]
    plan_name = st["plan_name"]
    ts = datetime.datetime.fromtimestamp(st["time"])
    tbl.addRow((i, ts, scann, uid, plan_name))
print(tbl)
