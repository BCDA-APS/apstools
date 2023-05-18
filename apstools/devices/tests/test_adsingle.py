import databroker
from bluesky import plans as bp
from bluesky.run_engine import RunEngine

from ...tests import BLUESKY_MOUNT_PATH
from ...tests import MonitorCache


def test_stage(adsingle):
    mcache = MonitorCache("ERROR: capture not supported in Single mode")
    adsingle.hdf1.write_message.subscribe(mcache.receiver)
    adsingle.stage()
    adsingle.hdf1.write_message.unsubscribe_all()
    assert len(mcache.messages) == 0
    adsingle.hdf1.unstage()


def test_count_not_in_catalog(adsingle):
    cat = databroker.temp().v2
    RE = RunEngine({})
    RE.subscribe(cat.v1.insert)

    # Acquire one image and save to HDF5 file.
    uids = RE(bp.count([adsingle]))
    assert len(uids) == 1
    assert len(cat) == 1

    ioc_file = adsingle.hdf1.full_file_name.get()
    assert len(ioc_file) > 0

    # Test the file is not known by the databroker
    assert len(cat[-1].primary.read()) == 0  # no image data

    # Test the file is found
    f = BLUESKY_MOUNT_PATH.parent / ioc_file.lstrip("/")
    assert f.exists()
