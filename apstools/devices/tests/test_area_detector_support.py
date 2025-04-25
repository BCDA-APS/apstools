"""
Test code where users control the names of the image files using EPICS.
"""

import datetime
import pathlib
import random
import tempfile
import time
from contextlib import nullcontext as does_not_raise

import bluesky
import pytest
from bluesky import plan_stubs as bps
from bluesky import plans as bp

from ...tests import IOC_AD
from ...tests import READ_PATH_TEMPLATE
from ...tests import WRITE_PATH_TEMPLATE
from ...tests import MonitorCache
from ...tests import timed_pause
from .. import AD_EpicsFileNameHDF5Plugin
from .. import AD_EpicsFileNameJPEGPlugin
from .. import AD_EpicsFileNameMixin
from .. import AD_EpicsFileNameTIFFPlugin
from .. import AD_full_file_name_local
from .. import AD_plugin_primed
from .. import AD_prime_plugin2
from .. import BadPixelPlugin
from .. import ad_creator


def custom_ad_creator(plugin_name):
    """Create area detector with named file writer plugin."""
    plugin_class = dict(
        hdf1=AD_EpicsFileNameHDF5Plugin,
        jpeg1=AD_EpicsFileNameJPEGPlugin,
        tiff1=AD_EpicsFileNameTIFFPlugin,
    )
    writer_plugin = {
        plugin_name: {
            "class": plugin_class[plugin_name],
            "write_path_template": WRITE_PATH_TEMPLATE,
            "read_path_template": READ_PATH_TEMPLATE,
        }
    }
    if plugin_name in "jpeg1 tiff1".split():
        writer_plugin[plugin_name]["suffix"] = f"{plugin_name.upper()}:"
    adsimdet = ad_creator(
        IOC_AD,
        name="adsimdet",
        class_name="MySimDet",
        plugins=[
            "cam",
            "image",
            "pva",
            writer_plugin,
        ],
    )
    return adsimdet


@pytest.mark.parametrize(
    # fmt: off
    "plugin_name, spec",
    [
        ["hdf1", "AD_HDF5"],
        ["jpeg1", "AD_JPEG"],
        ["tiff1", "AD_TIFF"],
    ],
    # fmt: on
)
def test_AD_EpicsFileNameMixin(plugin_name, spec):
    adsimdet = custom_ad_creator(plugin_name)
    assert adsimdet is not None
    assert plugin_name in dir(adsimdet)

    # basic plugin tests
    mixin = getattr(adsimdet, plugin_name)
    assert AD_EpicsFileNameMixin is not None
    assert isinstance(mixin, AD_EpicsFileNameMixin)
    assert "filestore_spec" in dir(mixin)
    assert mixin.filestore_spec == spec
    assert isinstance(mixin.stage_sigs, dict)
    assert len(mixin.stage_sigs) >= 4
    assert "capture" in mixin.stage_sigs

    # configuration prescribed for the user
    user_settings = dict(
        array_counter=0,
        auto_increment=1,  # Yes
        auto_save=1,  # Yes
        create_directory=-5,
        file_name="flotsam",
        file_number=1 + int(10 * random.random()),
        file_path=f"{pathlib.Path(tempfile.mkdtemp())}/",  # ALWAYS ends with "/"
        file_template=f"%s%s_%2.2d.{plugin_name}",
        num_capture=1 + int(10 * random.random()),
    )
    if plugin_name == "hdf1":
        user_settings["compression"] = "zlib"

    # add the settings
    for k, v in user_settings.items():
        getattr(mixin, k).put(v)
    timed_pause()

    adsimdet.stage()
    if plugin_name == "hdf1":  # Why special case?
        user_settings["file_number"] += 1  # the IOC will do the same
    assert list(mixin.stage_sigs.keys())[-1] == "capture"
    for k, v in user_settings.items():
        assert getattr(mixin, k).get() == v, f"{plugin_name=} {k=}  {v=}"

    assert mixin.get_frames_per_point() == user_settings["num_capture"]

    filename, read_path, write_path = mixin.make_filename()
    assert isinstance(filename, str)
    assert isinstance(read_path, str)
    assert isinstance(write_path, str)
    assert filename == user_settings["file_name"]
    assert read_path.startswith(datetime.datetime.now().strftime(READ_PATH_TEMPLATE))
    assert write_path == user_settings["file_path"]
    adsimdet.unstage()


@pytest.mark.parametrize(
    "plugin_name, plugin_class",
    [
        ["hdf1", AD_EpicsFileNameHDF5Plugin],
        ["jpeg1", AD_EpicsFileNameJPEGPlugin],
        ["tiff1", AD_EpicsFileNameTIFFPlugin],
    ],
)
def test_stage(plugin_name, plugin_class, adsimdet, fname):
    assert isinstance(plugin_name, str)

    plugin = getattr(adsimdet, plugin_name)
    assert isinstance(plugin, plugin_class)

    plugin.file_name.put(fname)
    time.sleep(0.2)
    assert fname == plugin.file_name.get(), "file name was not put()"

    plugin.stage()
    assert fname == plugin.file_name.get(), "file name was changed by stage()"

    plugin.unstage()
    assert fname == plugin.file_name.get(), "file name was changed by unstage()"


@pytest.mark.parametrize(
    "plugin_name, plugin_class",
    [
        ["hdf1", AD_EpicsFileNameHDF5Plugin],
        ["jpeg1", AD_EpicsFileNameJPEGPlugin],
        ["tiff1", AD_EpicsFileNameTIFFPlugin],
    ],
)
def test_bp_count_custom_name(plugin_name, plugin_class, fname):
    assert isinstance(plugin_name, str)

    adsimdet = custom_ad_creator(plugin_name)

    plugin = getattr(adsimdet, plugin_name)
    assert isinstance(plugin, plugin_class)

    def prepare_count(file_path, file_name, n_images):
        # fmt: off
        yield from bps.mv(
            plugin.array_counter, 0,
            plugin.auto_increment, "Yes",
            plugin.auto_save, "Yes",
            plugin.create_directory, -5,
            plugin.dropped_arrays, 0,
            plugin.file_name, file_name,
            plugin.file_path, file_path,
            plugin.num_capture, n_images,
            adsimdet.cam.num_images, n_images,
            adsimdet.cam.acquire_time, 0.001,
            adsimdet.cam.acquire_period, 0.002,
            adsimdet.cam.image_mode, "Single",
            plugin.file_template, "%s%s_%3.3d.h5"
        )
        # fmt: on

    RE = bluesky.RunEngine({})
    NUM_FRAMES = 1
    RE(prepare_count(f"{plugin.write_path_template}/", fname, NUM_FRAMES))
    assert plugin.auto_increment.get() in (1, "Yes")
    assert plugin.auto_save.get() in (1, "Yes")
    assert plugin.create_directory.get() == -5
    assert plugin.file_name.get() == fname
    assert plugin.file_path.get() == f"{plugin.write_path_template}/"
    assert plugin.file_template.get() not in ("", "/")
    assert plugin.num_capture.get() == NUM_FRAMES
    assert adsimdet.cam.num_images.get() == NUM_FRAMES
    assert adsimdet.cam.acquire_time.get() == 0.001
    assert adsimdet.cam.acquire_period.get() == 0.002
    assert adsimdet.cam.image_mode.get() in (0, "Single")

    # remember this for testing later
    next_file_number = plugin.file_number.get()

    # acquire the image (using standard technique)
    uids = RE(bp.count([adsimdet]))
    assert len(uids) == 1
    assert plugin.file_number.get() > next_file_number
    assert not adsimdet.cam.is_busy

    assert plugin.dropped_arrays.get() == 0
    assert plugin.array_counter.get() == NUM_FRAMES
    assert plugin.num_captured.get() == NUM_FRAMES

    # diagnostic per issue #696
    ffname = plugin.full_file_name.get(use_monitor=False).strip()
    if ffname in ("", "/"):
        # second chance, race condition?  don't trust the CA monitor cache
        ffname = plugin.full_file_name.get(use_monitor=False).strip()
    assert ffname not in ("", "/"), str(ffname)

    # local file-system image file name
    lfname = AD_full_file_name_local(plugin)
    assert lfname is not None
    assert lfname.exists(), lfname
    assert isinstance(lfname, pathlib.Path)
    assert fname in str(lfname), f"{lfname=}  {fname=}"


def test_full_file_name_local(fname):
    adsimdet = custom_ad_creator("hdf1")
    plugin = adsimdet.hdf1
    plugin.file_name.put(fname)
    plugin.file_path.put(f"{plugin.write_path_template}/")
    time.sleep(0.1)

    adsimdet.stage()  # creates the HDF5 file
    adsimdet.unstage()

    lfname = AD_full_file_name_local(plugin)
    assert lfname is not None, str(plugin)
    assert lfname.exists(), lfname
    assert isinstance(lfname, pathlib.Path)
    assert str(lfname).find(fname) > 0


def test_file_numbering(fname):
    adsimdet = custom_ad_creator("hdf1")
    plugin = adsimdet.hdf1
    plugin.file_name.put(fname)
    plugin.file_path.put(f"{plugin.write_path_template}/")
    time.sleep(0.1)
    assert fname == plugin.file_name.get(), "file name was not put()"

    assert "file_template" not in plugin.stage_sigs

    # prepare for file name with file number
    file_number = plugin.file_number.get()
    plugin.file_template.put("%s%s_%4.4d.h5")
    adsimdet.stage()
    adsimdet.unstage()
    full_file_name = plugin.full_file_name.get()
    assert isinstance(full_file_name, str)
    assert len(full_file_name) > 0
    assert full_file_name.find(fname) > 0, str(full_file_name)
    assert full_file_name.endswith(
        f"{fname}_{file_number:04d}.h5"
    ), f"{full_file_name=} {fname}_{file_number:04d}.h5"

    # prepare for file name with no file number
    file_number = plugin.file_number.get()
    plugin.file_template.put("%s%s.h5")
    time.sleep(0.1)
    adsimdet.stage()
    adsimdet.unstage()
    full_file_name = plugin.full_file_name.get()
    assert isinstance(full_file_name, str)
    assert full_file_name.find(fname) > 0, f"{fname=} {full_file_name=}"
    assert full_file_name.endswith(f"{fname}.h5"), f"{full_file_name=} {fname}.h5"


def test_capture_error_with_single_mode(adsimdet):
    # adsimdet = custom_ad_creator("hdf1")
    plugin = adsimdet.hdf1
    plugin.file_name.put("test")

    # test that plugin is in the wrong configuration for Single mode
    assert "capture" in plugin.stage_sigs
    assert list(plugin.stage_sigs)[-1] == "capture"
    assert "file_write_mode" in plugin.stage_sigs
    assert plugin.file_write_mode.enum_strs[0] == "Single"
    assert plugin.stage_sigs["file_write_mode"] == "Stream"

    # Test for this reported error message.
    err_message = "ERROR: capture not supported in Single mode"

    # Error was corrected in issue #823.
    # A lot happens during device staging. The error message is posted and then
    # quickly cleared as the IOC responds to other items staged.  Collect this
    # transient message using a callback for later examination.
    mcache = MonitorCache(err_message)

    plugin.write_message.subscribe(mcache.receiver)
    plugin.stage()
    plugin.write_message.unsubscribe_all()
    assert len(mcache.messages) == 0
    plugin.unstage()


def test_single_mode(adsingle):
    err_message = "ERROR: capture not supported in Single mode"
    mcache = MonitorCache(err_message)

    plugin = adsingle.hdf1
    plugin.file_write_mode.put("Stream")
    plugin.num_capture.put(0)

    plugin.write_message.subscribe(mcache.receiver)
    plugin.stage()
    plugin.write_message.unsubscribe_all()
    assert len(mcache.messages) == 0
    plugin.unstage()


@pytest.mark.parametrize(
    "Klass, setup, attrs, context, expected",
    [
        [BadPixelPlugin, {}, ["file_name"], does_not_raise(), None],
    ],
)
def test_plugin(Klass, setup, attrs, context, expected):
    """Basic unit testing of plugin classes, no connection needed."""
    with context as exinfo:
        obj = Klass("test:", name="test", **setup)
        knowns = dir(obj)
        for attr in attrs:
            assert attr in knowns  # hasattr() needs connection

    if expected is not None:
        assert expected in str(exinfo)


@pytest.mark.parametrize(
    "setup",
    [
        dict(
            plugins=[
                "cam",
                dict(
                    hdf1={
                        "class": AD_EpicsFileNameHDF5Plugin,
                        "read_path_template": "/tmp/docker_ioc/iocad/tmp/",
                        "write_path_template": "/tmp/",
                    }
                ),
            ]
        ),
    ],
)
@pytest.mark.parametrize(
    "attrs, context, expected",
    [
        [
            dict(
                auto_save="No",
                create_directory=0,
                file_name="",
                file_number=1,
                file_path="",
                file_template="",
            ),
            pytest.raises(ValueError),
            "'ad:HDF1:FileName' is an empty string.",
        ],
        [
            dict(
                auto_save="No",
                create_directory=-5,
                file_template="",
                file_name="test",
                file_number=1,
                file_path="",
            ),
            pytest.raises(ValueError),
            "'ad:HDF1:FilePath' is an empty string.",
        ],
        [
            dict(
                auto_save="No",
                create_directory=-5,
                file_template="",
                file_name="test",
                file_number=1,
                file_path="/tmp/",
            ),
            pytest.raises(ValueError),
            "'ad:HDF1:FileTemplate' is an empty string.",
        ],
        [
            dict(
                auto_save="No",
                create_directory=-5,
                file_template="%s%s_%6.6d.h5",
                file_name="test",
                file_number=1,
                file_path="/tmp/",
            ),
            does_not_raise(),
            None,
        ],
        [
            dict(
                auto_save="No",
                create_directory=-5,
                file_template="%s%s_%6.6d.h5",
                file_name="test",
                file_number=1,
                file_path="/",
            ),
            pytest.raises(OSError),
            "Path '/' does not exist on IOC",
        ],
    ],
)
def test_HDF5plugin_i1062(setup, attrs, context, expected):
    """Issue #1062, Unconfigured HDF plugin."""
    import epics

    # Caller is responsible for setting values of these Components:
    # * array_counter
    # * auto_increment
    # * auto_save
    # * compression (only HDF)
    # * create_directory
    # * file_name
    # * file_number
    # * file_path
    # * file_template
    # * num_capture

    with context as exinfo:
        det = ad_creator(IOC_AD, name="det", **setup)

        # Confirm these attributes are not staged.
        for attr in "file_name file_path file_template".split():
            assert attr not in det.hdf1.stage_sigs

        # # un-prime the HDF5 plugin
        # det.cam.data_type.put("Int8")
        # AD_prime_plugin2(det.hdf1)
        # det.cam.data_type.put("UInt8")
        # time.sleep(0.1)
        # assert not AD_plugin_primed(det.hdf1)

        if not AD_plugin_primed(det.hdf1):
            AD_prime_plugin2(det.hdf1)
            assert AD_plugin_primed(det.hdf1)

        for attr, value in attrs.items():
            epics.caput(getattr(det.hdf1, attr)._write_pv.pvname, value)

        # # This happens during det.hdf1.stage()
        # filename, read_path, write_path = det.hdf1.make_filename()
        # # Test its results.
        # formatter = datetime.datetime.now().strftime
        # assert filename == det.hdf1.file_name.get()
        # assert read_path == setup["plugins"][1]["hdf1"]["read_path_template"]
        # assert read_path == formatter(det.hdf1.read_path_template)
        # assert write_path == formatter(det.hdf1.file_path.get())

        RE = bluesky.RunEngine()
        (uid,) = RE(bp.count([det]))
        assert isinstance(uid, str)

    if expected is not None:
        assert expected in str(exinfo)
