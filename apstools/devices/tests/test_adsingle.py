import databroker
from bluesky import plans as bp
from bluesky.run_engine import RunEngine

from ...tests import MonitorCache
from ...tests import timed_pause


def test_stage(adsingle):
    mcache = MonitorCache("ERROR: capture not supported in Single mode")
    adsingle.hdf1.write_message.subscribe(mcache.receiver)
    adsingle.stage()
    adsingle.hdf1.write_message.unsubscribe_all()
    assert len(mcache.messages) == 0
    adsingle.hdf1.unstage()


def test_count(adsingle):
    cat = databroker.temp().v2
    RE = RunEngine({})
    RE.subscribe(cat.v1.insert)
    uids = RE(bp.count([adsingle]))
    assert len(uids) == 1
    
    # TODO: test the file is not known by databroker
    # TODO: test the file is found
