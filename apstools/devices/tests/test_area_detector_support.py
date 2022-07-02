from ...devices.area_detector_support import AD_EpicsFileNameHDF5Plugin
from ...devices.area_detector_support import AD_full_file_name_local
from ...devices.area_detector_support import AD_prime_plugin2
from ophyd import EpicsSignalWithRBV
from ophyd.areadetector import ADComponent
from ophyd.areadetector import DetectorBase
from ophyd.areadetector import SingleTrigger
from ophyd.areadetector.plugins import ImagePlugin_V34 as ImagePlugin
from ophyd.areadetector.plugins import PvaPlugin_V34 as PvaPlugin
from ophyd.areadetector import SimDetectorCam
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


class MyFixedCam(SimDetectorCam):
    pool_max_buffers = None
    offset = ADComponent(EpicsSignalWithRBV, "Offset")


class MySimDetector(SingleTrigger, DetectorBase):
    """ADSimDetector"""

    cam = ADComponent(MyFixedCam, "cam1:")
    image = ADComponent(ImagePlugin, "image1:")
    hdf1 = ADComponent(
        AD_EpicsFileNameHDF5Plugin,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )
    pva = ADComponent(PvaPlugin, "Pva1:")


@pytest.fixture(scope="function")
def adsimdet():
    "EPICS ADSimDetector."
    adsimdet = MySimDetector(IOC, name="adsimdet")
    adsimdet.wait_for_connection(timeout=15)
    adsimdet.read_attrs.append("hdf1")
    AD_prime_plugin2(adsimdet.hdf1)
    adsimdet.hdf1.create_directory.put(-5)
    yield adsimdet


@pytest.fixture(scope="function")
def fname():
    "File (base) name."
    dt = datetime.datetime.now()
    fname = f"test-image-{dt.minute:02d}-{dt.second:02d}"
    yield fname


def test_stage(adsimdet, fname):
    adsimdet.hdf1.file_name.put(fname)
    adsimdet.hdf1.file_path.put(f"{adsimdet.hdf1.write_path_template}/")
    time.sleep(0.2)
    assert fname == adsimdet.hdf1.file_name.get(), "file name was not put()"

    adsimdet.stage()
    assert fname == adsimdet.hdf1.file_name.get(), "file name was changed by stage()"

    adsimdet.unstage()
    assert fname == adsimdet.hdf1.file_name.get(), "file name was changed by unstage()"


def test_full_file_name_local(adsimdet, fname):
    adsimdet.hdf1.file_name.put(fname)
    adsimdet.hdf1.file_path.put(f"{adsimdet.hdf1.write_path_template}/")
    time.sleep(0.1)
    assert fname == adsimdet.hdf1.file_name.get(), "file name was not put()"

    adsimdet.stage()
    assert fname == adsimdet.hdf1.file_name.get(), "file name was changed by stage()"

    adsimdet.unstage()
    assert fname == adsimdet.hdf1.file_name.get(), "file name was changed by unstage()"

    lfname = AD_full_file_name_local(adsimdet.hdf1)
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
    adsimdet.hdf1.file_name.put(fname)
    adsimdet.hdf1.file_path.put(f"{adsimdet.hdf1.write_path_template}/")
    time.sleep(0.1)
    assert fname == adsimdet.hdf1.file_name.get(), "file name was not put()"

    assert adsimdet.hdf1.stage_sigs["file_template"] == "%s%s_%4.4d.h5"

    # prepare for file name with file number
    file_number = adsimdet.hdf1.file_number.get()
    adsimdet.stage()
    adsimdet.unstage()
    full_file_name = adsimdet.hdf1.full_file_name.get()
    assert isinstance(full_file_name, str)
    assert full_file_name.find(fname) > 0
    assert full_file_name.endswith(f"{fname}_{file_number:04d}.h5") > 0

    # prepare for file name with no file number
    adsimdet.hdf1.stage_sigs["file_template"] = "%s%s.h5"
    adsimdet.stage()
    adsimdet.unstage()
    full_file_name = adsimdet.hdf1.full_file_name.get()
    assert isinstance(full_file_name, str)
    assert full_file_name.find(fname) > 0
    assert full_file_name.endswith(f"{fname}.h5") > 0
