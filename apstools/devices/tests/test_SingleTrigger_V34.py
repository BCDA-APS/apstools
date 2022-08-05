from .. import AD_EpicsFileNameHDF5Plugin
from .. import AD_plugin_primed
from .. import AD_prime_plugin2
from .. import SingleTrigger_V34
from .. import CamMixin_V34
from ophyd.areadetector import ADComponent
from ophyd.areadetector import DetectorBase
from ophyd.areadetector import SimDetectorCam
from packaging import version
import pathlib


IOC = "ad:"
IMAGE_DIR = "adsimdet/%Y/%m/%d"
AD_IOC_MOUNT_PATH = pathlib.Path("/tmp")
BLUESKY_MOUNT_PATH = pathlib.Path("/tmp/docker_ioc/iocad/tmp")

# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / IMAGE_DIR}/"


class SimDetectorCam_V34(CamMixin_V34, SimDetectorCam):
    """triggering configuration and AcquireBusy support"""


class SimDetector_V34(SingleTrigger_V34, DetectorBase):
    """ADSimDetector"""

    cam = ADComponent(SimDetectorCam_V34, "cam1:")
    hdf1 = ADComponent(
        AD_EpicsFileNameHDF5Plugin,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )


def test_cam_mixin_v34_structure():
    adsimdet = SimDetector_V34(IOC, name="adsimdet")
    assert isinstance(adsimdet, DetectorBase)
    assert isinstance(adsimdet.cam, SimDetectorCam_V34)
    assert version.parse(adsimdet.cam._cam_release) >= version.parse("3.4")
    assert adsimdet._acquisition_busy_signal != adsimdet._acquisition_signal
    assert adsimdet.cam.pool_max_buffers is None
    for attr_name in "acquire_busy offset wait_for_plugins".split():
        assert hasattr(adsimdet.cam, attr_name), attr_name
        assert attr_name in adsimdet.cam.component_names, attr_name


def test_cam_mixin_v34_operation():
    adsimdet = SimDetector_V34(IOC, name="adsimdet")
    adsimdet.wait_for_connection()
    assert adsimdet.connected

    if not AD_plugin_primed(adsimdet.hdf1):
        AD_prime_plugin2(adsimdet.hdf1)
    assert AD_plugin_primed(adsimdet.hdf1)

    adsimdet.read_attrs.append("hdf1")
    # TODO: configure stage_sigs
    # TODO: acquire 10 frames with hdf1
    # TODO: test that all 10 frames were acquired
