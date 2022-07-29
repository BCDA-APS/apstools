""" FIXME:
(bluesky_2022_3) prjemian@zap:~/.../BCDA-APS/apstools$ pytest -vvv --lf ./apstools/devices/tests/test_area_detector_support.py
...
apstools/devices/area_detector_support.py:418: ValueError
============================================================== short test summary info ===============================================================
FAILED apstools/devices/tests/test_area_detector_support.py::test_stage[tiff1-AD_EpicsFileNameTIFFPlugin] - OSError: Path '/' does not exist on IOC.
FAILED apstools/devices/tests/test_area_detector_support.py::test_acquire[jpeg1-AD_EpicsFileNameJPEGPlugin] - ValueError: incomplete format
FAILED apstools/devices/tests/test_area_detector_support.py::test_acquire[tiff1-AD_EpicsFileNameTIFFPlugin] - AttributeError: 'NoneType' object has...
FAILED apstools/devices/tests/test_area_detector_support.py::test_full_file_name_local - ValueError: incomplete format
FAILED apstools/devices/tests/test_area_detector_support.py::test_file_numbering - ValueError: incomplete format
========================================================== 5 failed, 4 deselected in 7.88s ===========================================================
============================================================== short test summary info ===============================================================
FAILED apstools/devices/tests/test_area_detector_support.py::test_acquire[jpeg1-AD_EpicsFileNameJPEGPlugin] - AttributeError: 'NoneType' object has...
FAILED apstools/devices/tests/test_area_detector_support.py::test_acquire[tiff1-AD_EpicsFileNameTIFFPlugin] - AttributeError: 'NoneType' object has...
FAILED apstools/devices/tests/test_area_detector_support.py::test_file_numbering - AssertionError: assert False > 0
===================================================== 3 failed, 2 passed, 4 deselected in 19.05s =====================================================
"""

from ...devices import AD_EpicsFileNameHDF5Plugin
from ...devices import AD_EpicsFileNameJPEGPlugin
from ...devices import AD_EpicsFileNameTIFFPlugin
from ...devices import AD_full_file_name_local
from ...devices import AD_prime_plugin2
from ophyd import EpicsSignalWithRBV
from ophyd.areadetector import ADComponent
from ophyd.areadetector import DetectorBase
from ophyd.areadetector import SingleTrigger
from ophyd.areadetector.plugins import ImagePlugin_V34 as ImagePlugin
from ophyd.areadetector.plugins import PvaPlugin_V34 as PvaPlugin
from ophyd.areadetector import SimDetectorCam
from ophyd.signal import EpicsSignalBase
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
        timeout=60,
        write_timeout=60,
        connection_timeout=60,
    )
except RuntimeError:
    pass  # ignore if some EPICS object already created


class MyFixedCam(SimDetectorCam):
    pool_max_buffers = None
    offset = ADComponent(EpicsSignalWithRBV, "Offset")


class MySimDetector(SingleTrigger, DetectorBase):
    """ADSimDetector"""

    cam = ADComponent(MyFixedCam, "cam1:")
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
    adsimdet.wait_for_connection(timeout=15)
    for plugin_name in "hdf1 jpeg1 tiff1".split():
        adsimdet.read_attrs.append(plugin_name)
        plugin = getattr(adsimdet, plugin_name)
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
def test_acquire(plugin_name, plugin_class, adsimdet, fname):
    assert isinstance(plugin_name, str)

    plugin = getattr(adsimdet, plugin_name)
    assert isinstance(plugin, plugin_class)

    plugin.file_name.put(fname)
    ext = dict(hdf1="h5", jpeg1="jpg", tiff1="tif")[plugin_name]
    plugin.file_template.put(f"%s%s_%4.4d.{ext}")
    time.sleep(0.2)

    adsimdet.stage()
    adsimdet.trigger()
    time.sleep(0.005)
    while adsimdet.cam.acquire.get(use_monitor=False) not in (0, "Done"):
        time.sleep(0.005)
    adsimdet.unstage()

    lfname = AD_full_file_name_local(plugin)
    assert lfname is not None
    assert lfname.exists(), lfname
    assert isinstance(lfname, pathlib.Path)
    assert str(lfname).find(fname) > 0, f"{lfname=}  {fname=}"


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
    assert str(exc.value).endswith("'' does not exist on IOC.")
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
    # stage it: show that does not work
    file_number = plugin.file_number.get()
    plugin.stage_sigs["file_template"] = "%s%s.h5"
    adsimdet.stage()
    adsimdet.unstage()
    full_file_name = plugin.full_file_name.get()
    assert isinstance(full_file_name, str)
    assert full_file_name.find(fname) > 0
    # still not changed
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
