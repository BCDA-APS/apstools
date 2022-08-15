"""
Test code where users control the names of the image files using EPICS.
"""

from .. import AD_EpicsFileNameHDF5Plugin
from .. import AD_EpicsFileNameJPEGPlugin
from .. import AD_EpicsFileNameTIFFPlugin
from .. import AD_full_file_name_local
from .. import AD_plugin_primed
from .. import AD_prime_plugin2
from .. import CamMixin_V34 as CamMixin
from .. import SingleTrigger_V34 as SingleTrigger
from ...tests import MASTER_TIMEOUT
from ophyd.areadetector import ADComponent
from ophyd.areadetector import DetectorBase
from ophyd.areadetector import SimDetectorCam
from ophyd.areadetector.plugins import ImagePlugin_V34 as ImagePlugin
from ophyd.areadetector.plugins import PvaPlugin_V34 as PvaPlugin
from ophyd.signal import EpicsSignalBase
import bluesky
import bluesky.plan_stubs as bps
import bluesky.plans as bp
import datetime
import pathlib
import pytest
import time


IOC = "ad:"
IMAGE_DIR = "adsimdet/%Y/%m/%d"
AD_IOC_MOUNT_PATH = pathlib.Path("/tmp")
BLUESKY_MOUNT_PATH = pathlib.Path("/tmp/docker_ioc/iocad/tmp")

# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / IMAGE_DIR}/"


# set default timeout for all EpicsSignal connections & communications
try:
    EpicsSignalBase.set_defaults(
        auto_monitor=True,
        timeout=MASTER_TIMEOUT,
        write_timeout=MASTER_TIMEOUT,
        connection_timeout=MASTER_TIMEOUT,
    )
except RuntimeError:
    pass  # ignore if some EPICS object already created


class MySimDetectorCam(CamMixin, SimDetectorCam):
    """triggering configuration and AcquireBusy support"""


class MySimDetector(SingleTrigger, DetectorBase):
    """ADSimDetector"""

    cam = ADComponent(MySimDetectorCam, "cam1:")
    hdf1 = ADComponent(
        AD_EpicsFileNameHDF5Plugin,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )
    image = ADComponent(ImagePlugin, "image1:")
    jpeg1 = ADComponent(
        AD_EpicsFileNameJPEGPlugin,
        "JPEG1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )
    pva = ADComponent(PvaPlugin, "Pva1:")
    tiff1 = ADComponent(
        AD_EpicsFileNameTIFFPlugin,
        "TIFF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )


@pytest.fixture(scope="function")
def adsimdet():
    "EPICS ADSimDetector."
    adsimdet = MySimDetector(IOC, name="adsimdet")
    adsimdet.stage_sigs["cam.wait_for_plugins"] = "Yes"
    adsimdet.wait_for_connection(timeout=15)
    for plugin_name in "hdf1 jpeg1 tiff1".split():
        adsimdet.read_attrs.append(plugin_name)
        plugin = getattr(adsimdet, plugin_name)
        if not AD_plugin_primed(plugin):
            AD_prime_plugin2(plugin)

        # these settings are the caller's responsibility
        plugin.file_name.put("")  # control this in tests
        plugin.create_directory.put(-5)
        plugin.file_path.put(f"{plugin.write_path_template}/")
        ext = dict(hdf1="h5", jpeg1="jpg", tiff1="tif")[plugin_name]
        plugin.file_template.put(f"%s%s_%4.4d.{ext}")
        plugin.auto_increment.put("Yes")
        plugin.auto_save.put("Yes")
        if plugin_name == "hdf1":
            plugin.compression.put("zlib")
            plugin.zlevel.put(6)
        elif plugin_name == "jpeg":
            plugin.jpeg_quality.put(50)
    yield adsimdet


@pytest.fixture(scope="function")
def fname():
    "File (base) name."
    dt = datetime.datetime.now()
    fname = f"test-image-{dt.minute:02d}-{dt.second:02d}"
    yield fname


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
def test_bp_count_custom_name(plugin_name, plugin_class, adsimdet, fname):
    assert isinstance(plugin_name, str)

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
            # plugin.file_template  # pre-configured
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
    ffname = plugin.full_file_name.get().strip()
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


def test_full_file_name_local(adsimdet, fname):
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


def test_no_file_path(adsimdet, fname):
    adsimdet.hdf1.file_name.put(fname)
    adsimdet.hdf1.file_path.put("/no-such-path-exists")
    time.sleep(0.1)
    assert adsimdet.hdf1.file_path_exists.get() == 0

    adsimdet.hdf1.file_path.put("")
    time.sleep(0.1)
    assert adsimdet.hdf1.file_path_exists.get() == 0

    with pytest.raises(OSError) as exc:
        adsimdet.stage()
    assert str(exc.value).endswith(" does not exist on IOC.")
    adsimdet.unstage()


def test_file_numbering(adsimdet, fname):
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
