import pathlib
import tempfile

import bluesky.plans as bp
import databroker
import pytest
from bluesky import RunEngine
from ophyd import Component
from ophyd import EpicsMotor
from ophyd.areadetector import DetectorBase
from ophyd.areadetector import SimDetectorCam
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector.plugins import HDF5Plugin
from ophyd.areadetector.plugins import ImagePlugin

from ...devices import AD_plugin_primed
from ...devices import AD_prime_plugin2
from ...devices import CamMixin_V34 as CamMixin
from ...devices import SingleTrigger_V34 as SingleTrigger
from .. import NXWriter

AD_IOC = "ad:"
MOTOR_PV = "gp:m1"
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

    image = Component(ImagePlugin, "image1:")
    cam = Component(MySimDetectorCam, "cam1:")

    hdf1 = Component(
        HDF5PluginWithFileStore,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
        read_attrs=[],
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.hdf1.write_path_template = WRITE_PATH_TEMPLATE
        self.hdf1.read_path_template = READ_PATH_TEMPLATE


@pytest.fixture(scope="function")
def camera():
    """EPICS ADSimDetector."""
    camera = MyDetector(
        AD_IOC,
        name="camera",
        read_attrs=["hdf1"],
    )
    camera.wait_for_connection(timeout=15)
    if not AD_plugin_primed(camera.hdf1):
        AD_prime_plugin2(camera.hdf1)
    camera.cam.acquire_period.put(0.1)
    camera.cam.acquire_time.put(0.1)
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
    nxwriter.warn_on_missing_content = False

    RE = RunEngine()
    RE.subscribe(catalog.v1.insert)
    RE.subscribe(nxwriter.receiver)

    uids = RE(bp.scan([camera], motor, -0.1, 0, 3))
    assert isinstance(uids, (list, tuple))
    assert len(uids) == 1
    assert uids[-1] in catalog
    assert test_file.exists()
