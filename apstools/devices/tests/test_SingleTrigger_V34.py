import pathlib

import bluesky
import bluesky.plans as bp
import databroker
from ophyd import ADComponent
from ophyd import DetectorBase
from ophyd import EpicsSignal
from ophyd import SimDetectorCam
from ophyd import SingleTrigger
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector.plugins import HDF5Plugin_V34 as HDF5Plugin
from ophyd.areadetector.plugins import ImagePlugin_V34 as ImagePlugin
from packaging import version

from ...tests import IOC_AD
from .. import AD_plugin_primed
from .. import CamMixin_V34
from .. import SimDetectorCam_V34
from .. import SingleTrigger_V34
from .. import ensure_AD_plugin_primed

IMAGE_DIR = "adsimdet/%Y/%m/%d"
AD_IOC_MOUNT_PATH = pathlib.Path("/tmp")
BLUESKY_MOUNT_PATH = pathlib.Path("/tmp/docker_ioc/iocad/tmp")

# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / IMAGE_DIR}/"


class MyHDF5Plugin(FileStoreHDF5IterativeWrite, HDF5Plugin):
    """
    Add data acquisition methods to HDF5Plugin.

    * ``stage()`` - prepare device PVs befor data acquisition
    * ``unstage()`` - restore device PVs after data acquisition
    * ``generate_datum()`` - coordinate image storage metadata
    """

    def stage(self):
        self.stage_sigs.move_to_end("capture", last=True)
        super().stage()


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
    adsimdet = SimDetector_V34(IOC_AD, name="adsimdet")
    assert isinstance(adsimdet, DetectorBase)
    assert isinstance(adsimdet.cam, SimDetectorCam_V34)
    assert version.parse(adsimdet.cam._cam_release) >= version.parse("3.4")
    assert adsimdet._acquisition_busy_signal != adsimdet._acquisition_signal
    assert adsimdet.cam.pool_max_buffers is None
    for attr_name in "acquire_busy offset wait_for_plugins".split():
        assert hasattr(adsimdet.cam, attr_name), attr_name
        assert attr_name in adsimdet.cam.component_names, attr_name


def test_the_old_way():
    class MyFixedCam(SimDetectorCam):
        "No need to add unused, new attributes such as offset."

        pool_max_buffers = None

    class OldHDF5Plugin(FileStoreHDF5IterativeWrite, HDF5Plugin):
        pass

    class Phoenix(SingleTrigger, DetectorBase):
        cam = ADComponent(MyFixedCam, "cam1:")
        hdf1 = ADComponent(
            OldHDF5Plugin,
            "HDF1:",
            write_path_template=WRITE_PATH_TEMPLATE,
            read_path_template=READ_PATH_TEMPLATE,
        )
        image = ADComponent(ImagePlugin, "image1:")

    adsimdet = Phoenix(IOC_AD, name="adsimdet")
    adsimdet.wait_for_connection(timeout=15)
    assert adsimdet.connected

    adsimdet.read_attrs.append("hdf1")
    adsimdet.hdf1.create_directory.put(-5)

    NUM_FRAMES = 1
    adsimdet.cam.stage_sigs["acquire_time"] = 0.1
    adsimdet.cam.stage_sigs["image_mode"] = "Multiple"
    adsimdet.cam.stage_sigs["num_images"] = NUM_FRAMES
    adsimdet.hdf1.stage_sigs.move_to_end("capture")

    ensure_AD_plugin_primed(adsimdet.hdf1, True)
    assert AD_plugin_primed(adsimdet.hdf1)

    cat = databroker.temp().v2
    RE = bluesky.RunEngine({})
    RE.subscribe(cat.v1.insert)

    # acquire the image (using standard technique)
    uids = RE(bp.count([adsimdet]))
    assert len(uids) == 1

    run = cat.v2[uids[0]]
    assert run is not None

    dataset = run.primary.read()
    assert dataset is not None

    image = dataset["adsimdet_image"]
    assert image is not None
    assert len(image.shape) == 4
    assert image.shape == (1, NUM_FRAMES, 1024, 1024)


def test_ignore_no_WaitForPlugins():
    """This is the old way (pre AD 3.1)."""

    class MyFixedCam(SimDetectorCam):
        "No need to add unused, new attributes such as offset."

        pool_max_buffers = None

    class OldHDF5Plugin(FileStoreHDF5IterativeWrite, HDF5Plugin):
        pass

    class ThisSimDetector(SingleTrigger, DetectorBase):
        """Custom ADSimDetector."""

        cam = ADComponent(MyFixedCam, "cam1:")
        hdf1 = ADComponent(
            OldHDF5Plugin,
            "HDF1:",
            write_path_template=WRITE_PATH_TEMPLATE,
            read_path_template=READ_PATH_TEMPLATE,
        )
        image = ADComponent(ImagePlugin, "image1:")

    adsimdet = ThisSimDetector(IOC_AD, name="adsimdet")
    adsimdet.wait_for_connection(timeout=15)
    assert adsimdet.connected

    adsimdet.read_attrs.append("hdf1")

    adsimdet.hdf1.create_directory.put(-5)

    NUM_FRAMES = 100
    adsimdet.cam.stage_sigs["acquire_period"] = 0.002
    adsimdet.cam.stage_sigs["acquire_time"] = 0.001
    adsimdet.cam.stage_sigs["image_mode"] = "Multiple"
    adsimdet.cam.stage_sigs["num_images"] = NUM_FRAMES

    # ('None', 'N-bit', 'szip', 'zlib', 'Blosc', 'BSLZ4', 'LZ4', 'JPEG')
    # LZ4 and others require 'import hdf5plugin'
    adsimdet.hdf1.stage_sigs["compression"] = "zlib"
    adsimdet.hdf1.stage_sigs["file_template"] = "%s%s_%3.3d.h5"

    # Can't use LazyOpen feature and access run.primary.read() using databroker.
    # Raises event_model.EventModelError: Error instantiating handler class
    #   <class 'area_detector_handlers.handlers.AreaDetectorHDF5Handler'>
    # adsimdet.hdf1.stage_sigs["lazy_open"] = 1

    adsimdet.hdf1.stage_sigs.move_to_end("capture")

    ensure_AD_plugin_primed(adsimdet.hdf1, True)

    cat = databroker.temp().v2
    RE = bluesky.RunEngine({})
    RE.subscribe(cat.v1.insert)

    # acquire the image (using standard technique)
    uids = RE(bp.count([adsimdet]))
    assert len(uids) == 1

    run = cat.v2[uids[0]]
    assert run is not None

    dataset = run.primary.read()
    assert dataset is not None

    image = dataset["adsimdet_image"]
    assert image is not None
    assert len(image.shape) == 4
    assert image.shape == (1, NUM_FRAMES, 1024, 1024)


def test_cam_mixin_v34_operation():
    adsimdet = SimDetector_V34(IOC_AD, name="adsimdet")
    adsimdet.wait_for_connection()
    assert adsimdet.connected

    ensure_AD_plugin_primed(adsimdet.hdf1, True)
    assert AD_plugin_primed(adsimdet.hdf1)

    adsimdet.read_attrs.append("hdf1")
    adsimdet.hdf1.create_directory.put(-5)

    NUM_FRAMES = 100
    adsimdet.cam.stage_sigs["acquire_period"] = 0.0021
    adsimdet.cam.stage_sigs["acquire_time"] = 0.001
    adsimdet.cam.stage_sigs["image_mode"] = "Multiple"
    adsimdet.cam.stage_sigs["num_images"] = NUM_FRAMES
    adsimdet.cam.stage_sigs["wait_for_plugins"] = "Yes"
    adsimdet.hdf1.stage_sigs["auto_increment"] = "Yes"
    adsimdet.hdf1.stage_sigs["auto_save"] = "Yes"
    adsimdet.hdf1.stage_sigs["blocking_callbacks"] = "No"
    adsimdet.hdf1.stage_sigs["compression"] = "zlib"
    adsimdet.hdf1.stage_sigs["file_template"] = "%s%s_%5.5d.h5"
    adsimdet.hdf1.stage_sigs["num_capture"] = 0  # means: capture ALL frames sent
    adsimdet.hdf1.stage_sigs["queue_size"] = 100

    # Can't use LazyOpen feature and access run.primary.read() using databroker.
    # Raises event_model.EventModelError: Error instantiating handler class
    #   <class 'area_detector_handlers.handlers.AreaDetectorHDF5Handler'>
    # adsimdet.hdf1.stage_sigs["lazy_open"] = 1

    adsimdet.image.stage_sigs["blocking_callbacks"] = "No"

    assert adsimdet.cam.stage_sigs["wait_for_plugins"] == "Yes"
    assert adsimdet.hdf1.stage_sigs["blocking_callbacks"] == "No"

    cat = databroker.temp().v2
    RE = bluesky.RunEngine({})
    RE.subscribe(cat.v1.insert)

    # acquire the image (using standard technique)
    uids = RE(bp.count([adsimdet]))
    assert len(uids) == 1
    assert not adsimdet.cam.is_busy
    assert adsimdet.hdf1.num_captured.get() == NUM_FRAMES

    expected_sigs = {
        adsimdet: {
            "cam.acquire": 0,
            "cam.image_mode": 1,
        },
        adsimdet.cam: {
            "acquire_period": 0.0021,
            "acquire_time": 0.001,
            "image_mode": "Multiple",
            "num_images": NUM_FRAMES,
            "wait_for_plugins": "Yes",
        },
        adsimdet.hdf1: {
            "array_counter": 0,
            "auto_increment": "Yes",
            "auto_save": "Yes",
            "blocking_callbacks": "No",
            "compression": "zlib",
            "create_directory": -3,
            "enable": 1,
            "file_template": "%s%s_%5.5d.h5",
            "file_write_mode": "Stream",
            "num_capture": 0,
            "parent.cam.array_callbacks": 1,
            "queue_size": 100,
            "capture": 1,
        },
        adsimdet.image: {
            "enable": 1,
            "blocking_callbacks": "No",
            "parent.cam.array_callbacks": 1,
        },
    }
    for obj, expected in expected_sigs.items():
        assert obj.stage_sigs == expected, str(obj)

    run = cat.v2[uids[0]]
    assert run is not None

    dataset = run.primary.read()
    assert dataset is not None

    image = dataset["adsimdet_image"]
    assert image is not None
    assert len(image.shape) == 4
    assert image.shape == (1, NUM_FRAMES, 1024, 1024)
