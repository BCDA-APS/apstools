import pathlib
import tempfile

import bluesky.plans as bp
import databroker
import h5py
import pytest
from bluesky import RunEngine
from ophyd import Component
from ophyd import EpicsMotor
from ophyd.areadetector import DetectorBase
from ophyd.areadetector import SimDetectorCam
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector.plugins import HDF5Plugin_V34 as HDF5Plugin
from ophyd.areadetector.plugins import ImagePlugin_V34 as ImagePlugin

from ...devices import ensure_AD_plugin_primed
from ...devices import CamMixin_V34 as CamMixin
from ...devices import SingleTrigger_V34 as SingleTrigger
from .. import NXWriter
from ...tests import IOC_GP
from ...tests import IOC_AD

MOTOR_PV = f"{IOC_GP}m1"
IMAGE_DIR = "adsimdet/%Y/%m/%d"
AD_IOC_MOUNT_PATH = pathlib.Path("/tmp")
BLUESKY_MOUNT_PATH = pathlib.Path("/tmp/docker_ioc/iocad/tmp")

# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / IMAGE_DIR}/"


class HDF5PluginWithFileStore(HDF5Plugin, FileStoreHDF5IterativeWrite):
    pass


class MySimDetectorCam(CamMixin, SimDetectorCam):
    """triggering configuration and AcquireBusy support"""


class MyDetector(SingleTrigger, DetectorBase):
    cam = Component(MySimDetectorCam, "cam1:")

    hdf1 = Component(
        HDF5PluginWithFileStore,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )
    image = Component(ImagePlugin, "image1:")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hdf1.write_path_template = WRITE_PATH_TEMPLATE
        self.hdf1.read_path_template = READ_PATH_TEMPLATE


@pytest.fixture(scope="function")
def camera():
    """EPICS ADSimDetector."""
    camera = MyDetector(IOC_AD, name="camera")
    camera.wait_for_connection(timeout=15)

    camera.hdf1.create_directory.put(-5)
    camera.hdf1.file_path.put(f"{WRITE_PATH_TEMPLATE}/")

    camera.read_attrs.append("cam")
    camera.read_attrs.append("hdf1")

    camera.cam.stage_sigs["acquire_period"] = 0.1
    camera.cam.stage_sigs["acquire_time"] = 0.1
    camera.cam.stage_sigs["num_images"] = 1
    camera.cam.stage_sigs["wait_for_plugins"] = "Yes"
    camera.hdf1.stage_sigs["blocking_callbacks"] = "No"
    camera.hdf1.stage_sigs["compression"] = "zlib"
    camera.hdf1.stage_sigs["num_capture"] = 0  # capture ALL frames received
    camera.hdf1.stage_sigs["zlevel"] = 6

    ensure_AD_plugin_primed(camera.hdf1, True)

    if "capture" in camera.hdf1.stage_sigs:
        camera.hdf1.stage_sigs.move_to_end("capture", last=True)
    yield camera


@pytest.fixture(scope="function")
def motor():
    """EPICS Motor"""
    motor = EpicsMotor(MOTOR_PV, name="motor")
    motor.wait_for_connection(timeout=5)
    yield motor


def test_stage_camera(camera):
    plugin = camera.hdf1
    assert "num_capture" in dir(plugin), f"{dir(plugin)=}"
    assert "num_capture" in plugin.stage_sigs
    assert plugin.create_directory.get() < -1, f"{plugin.create_directory.get()=}"
    assert len(plugin.write_path_template) > 0, f"{plugin.write_path_template.get()=}"
    assert len(plugin.read_path_template) > 0, f"{plugin.read_path_template.get()=}"
    assert len(plugin.file_path.get()) > 0, f"{plugin.file_path.get()=}"
    assert plugin.file_path.get().endswith("/"), f"{plugin.file_path.get()=}"
    assert list(plugin.stage_sigs.keys())[-1] == "capture", f"{plugin.stage_sigs=}"

    camera.stage()
    camera.unstage()
    assert True


def test_stage_motor(motor):
    motor.stage()
    motor.unstage()
    assert True


def test_NXWriter_with_RunEngine(camera, motor):
    test_file = pathlib.Path(tempfile.mkdtemp()) / "nxwriter.h5"
    catalog = databroker.temp().v2

    nxwriter = NXWriter()
    nxwriter.file_name = str(test_file)
    assert isinstance(nxwriter.file_name, pathlib.Path)
    nxwriter.warn_on_missing_content = False

    RE = RunEngine()
    RE.subscribe(catalog.v1.insert)
    RE.subscribe(nxwriter.receiver)

    npoints = 3
    uids = RE(bp.scan([camera], motor, -0.1, 0, npoints))
    assert isinstance(uids, (list, tuple))
    assert len(uids) == 1
    assert uids[-1] in catalog

    nxwriter.wait_writer()
    # time.sleep(1)  # wait just a bit longer

    assert test_file.exists()
    with h5py.File(test_file, "r") as root:
        default = root.attrs.get("default", "entry")
        assert default == "entry"
        assert default in root
        nxentry = root[default]

        default = nxentry.attrs.get("default", "data")
        assert default == "data"
        assert default in nxentry, f"{test_file=} {list(nxentry)=}"
        nxdata = nxentry[default]

        signal = nxdata.attrs.get("signal", "data")
        # assert signal == camera.name
        assert signal in nxdata
        frames = nxdata[signal]
        assert frames.shape == (npoints, 1024, 1024)
