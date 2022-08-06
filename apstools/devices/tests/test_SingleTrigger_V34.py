from .. import AD_plugin_primed
from .. import AD_prime_plugin2
from .. import CamMixin_V34
from .. import SingleTrigger_V34
from ophyd.areadetector import ADComponent
from ophyd.areadetector import DetectorBase
from ophyd.areadetector import SimDetectorCam
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector.plugins import HDF5Plugin_V34 as HDF5Plugin
from ophyd.areadetector.plugins import ImagePlugin_V34 as ImagePlugin
from packaging import version
import bluesky
import bluesky.plans as bp
import databroker
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

class MyHDF5Plugin(FileStoreHDF5IterativeWrite, HDF5Plugin):
    """docs"""

class SimDetector_V34(SingleTrigger_V34, DetectorBase):
    """ADSimDetector"""

    cam = ADComponent(SimDetectorCam_V34, "cam1:")
    hdf1 = ADComponent(
        MyHDF5Plugin,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )
    image = ADComponent(ImagePlugin, "image1:")


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
    adsimdet.hdf1.create_directory.put(-5)

    NUM_FRAMES = 10
    adsimdet.cam.stage_sigs["acquire_period"] = 0.105
    adsimdet.cam.stage_sigs["acquire_time"] = 0.1
    adsimdet.cam.stage_sigs["image_mode"] = "Multiple"
    adsimdet.cam.stage_sigs["num_images"] = NUM_FRAMES
    adsimdet.cam.stage_sigs["wait_for_plugins"] = "Yes"
    adsimdet.hdf1.stage_sigs["auto_increment"] = "Yes"
    adsimdet.hdf1.stage_sigs["auto_save"] = "Yes"
    adsimdet.hdf1.stage_sigs["blocking_callbacks"] = "No"
    adsimdet.hdf1.stage_sigs["compression"] = "zlib"
    adsimdet.hdf1.stage_sigs["lazy_open"] = 1
    adsimdet.hdf1.stage_sigs["num_capture"] = NUM_FRAMES
    adsimdet.hdf1.stage_sigs.move_to_end("capture")

    assert adsimdet.cam.stage_sigs["wait_for_plugins"] == "Yes"
    assert adsimdet.hdf1.stage_sigs["blocking_callbacks"] == "No"

    cat = databroker.temp().v2
    RE = bluesky.RunEngine({})
    RE.subscribe(cat.v1.insert)

    # acquire the image (using standard technique)
    uids = RE(bp.count([adsimdet]))
    assert len(uids) == 1
    assert not adsimdet.cam.is_busy

    run = cat.v2[uids[0]]
    assert run is not None

    dataset = run.primary.read()  # FIXME: cannot read the file as named,
    # resource_path is wrong, should end with "4fb5-bbc2_-000000.h5', "
    """
    E           event_model.EventModelError: Error instantiating handler class 
    <class 'area_detector_handlers.handlers.AreaDetectorHDF5Handler'> with 
    Resource document {
        'spec': 'AD_HDF5', 
        'root': '/', 
        'resource_path': 'tmp/docker_ioc/iocad/tmp/adsimdet/2022/08/05/f6d8d87b-dde9-4fb5-bbc2_-000001.h5', 
        'resource_kwargs': {
            'frame_per_point': 10
        }, 
        'path_semantics': 'posix', 
        'uid': '12e8c7b2-90e1-4721-bdaf-02c1d6c1dd1f', 
        'run_start': '9329adc9-6033-4955-aeea-8251cf7435d9'
    }. 
    Its 'root' field / was *not* modified by root_map.

    ../../../../micromamba/envs/bluesky_2022_3/lib/python3.9/site-packages/event_model/__init__.py:1052: EventModelError
    """
    assert dataset is not None

    image = dataset["adsimdet_image"]
    assert image is not None
    assert len(image.shape) == 4
    assert image.shape == (1, NUM_FRAMES, 1024, 1024)
