import pathlib
import tempfile
import time

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
    camera = MyDetector(AD_IOC, name="camera")
    camera.wait_for_connection(timeout=15)

    camera.read_attrs.append("cam")
    camera.read_attrs.append("hdf1")

    camera.cam.stage_sigs["acquire_period"] = 0.1
    camera.cam.stage_sigs["acquire_time"] = 0.1
    camera.cam.stage_sigs["num_images"] = 1
    # camera.cam.stage_sigs["num_capture"] = 0  # capture ALL frames received
    camera.cam.stage_sigs["wait_for_plugins"] = "Yes"
    camera.hdf1.stage_sigs["blocking_callbacks"] = "No"
    camera.hdf1.stage_sigs["compression"] = "zlib"
    camera.hdf1.stage_sigs["zlevel"] = 6

    if not AD_plugin_primed(camera.hdf1):
        print(f"Priming {camera.hdf1.dotted_name}")
        AD_prime_plugin2(camera.hdf1)

    if "capture" in camera.hdf1.stage_sigs:
        camera.hdf1.stage_sigs.move_to_end("capture", last=True)
    yield camera


@pytest.fixture(scope="function")
def motor():
    """EPICS Motor"""
    motor = EpicsMotor(MOTOR_PV, name="motor")
    motor.wait_for_connection(timeout=5)
    yield motor

# AssertionError: camera.hdf1.stage_sigs=OrderedDict(
#   [
#         ('enable', 1), 
#         ('create_directory', -3),
#         ('auto_increment', 'Yes'), 
#         ('array_counter', 0),
#         ('auto_save', 'Yes'), 
#         ('num_capture', 0), 
#         ('file_template', '%s%s_%6.6d.h5'), 
#         ('file_write_mode', 'Stream'), 
#         ('blocking_callbacks', 'No'), 
#         ('parent.cam.array_callbacks', 1), 
#         ('compression', 'zlib'), 
#         ('zlevel', 6), 
#         ('capture', 1)
#   ]
# )

def test_stage_camera(camera):
    plugin = camera.hdf1
    assert "num_capture" in dir(plugin), f"{dir(plugin)=}"
    if  "num_capture" in plugin.stage_sigs:
        plugin.stage_sigs.pop("num_capture")
    assert "num_capture" not in plugin.stage_sigs
    assert plugin.create_directory.get() < -1, f"{plugin.create_directory.get()=}"
    assert len(plugin.file_path.get()) > 0, f"{plugin.file_path.get()=}"
    assert len(plugin.write_path_template) > 0, f"{plugin.write_path_template.get()=}"
    assert len(plugin.read_path_template) > 0, f"{plugin.read_path_template.get()=}"
    assert plugin.file_path.get().endswith("/"), f"{plugin.file_path.get()=}"
    assert list(plugin.stage_sigs.keys())[-1] == "capture", f"{plugin.stage_sigs=}"

    camera.stage()
    camera.unstage()
    assert True

    assert False, f"{plugin.stage_sigs=}"


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

    npoints = 3
    uids = RE(bp.scan([camera], motor, -0.1, 0, npoints))
    assert isinstance(uids, (list, tuple))
    assert len(uids) == 1
    assert uids[-1] in catalog

    while nxwriter._writer_active:  # wait for the call back to finish
        time.sleep(nxwriter._external_file_read_retry_delay)

    assert test_file.exists()
    with h5py.File(test_file, "r") as root:
        default = root.attrs.get("default")
        assert default == "entry"
        assert default in root
        nxentry = root[default]

        default = nxentry.attrs.get("default")
        assert default == "data"
        assert default in nxentry
        nxdata = nxentry[default]

        signal = nxdata.attrs.get("signal")
        assert signal == camera.name
        assert signal in nxdata
        frames = nxdata[signal]
        assert frames.shape == (npoints, 1024, 1024)
