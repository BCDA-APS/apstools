import os
import ophyd
import ophyd.areadetector.filestore_mixins
import ophyd.areadetector.plugins
import pytest

from ... import utils

AD_IOC_PREFIX = "ad:"
GP_IOC_PREFIX = "gp:"
AD_IOC_FILES_ROOT = "/"
BLUESKY_FILES_ROOT = "/tmp/docker_ioc/ioc{AD_IOC_PREFIX.rstrip(':')}"
IOC_IMAGE_DIR = "/tmp/images/"
AD_IOC_PATH = os.path.join(AD_IOC_FILES_ROOT, IOC_IMAGE_DIR.lstrip("/"))
BLUESKY_PATH = os.path.join(BLUESKY_FILES_ROOT, IOC_IMAGE_DIR.lstrip("/"))


class MyCam(ophyd.SimDetectorCam):
    pool_max_buffers = None


class MyHDF5Plugin(
    ophyd.areadetector.filestore_mixins.FileStoreHDF5IterativeWrite,
    ophyd.areadetector.plugins.HDF5Plugin_V34
    # ophyd.HDF5Plugin
):
    pass


class MyFixedImagePlugin(ophyd.ImagePlugin):
    pool_max_buffers = None


class MyDetector(ophyd.SimDetector):
    cam = ophyd.ADComponent(MyCam, "cam1:")
    hdf1 = ophyd.ADComponent(
        MyHDF5Plugin,
        "HDF1:",
        write_path_template=AD_IOC_PATH,
        read_path_template=BLUESKY_PATH,
    )
    image = ophyd.ADComponent(MyFixedImagePlugin, "image1:")


gpm1 = ophyd.EpicsMotor(f"{GP_IOC_PREFIX}m1", name="gpm1")
simdet = MyDetector(AD_IOC_PREFIX, name="simdet")
gpm1.wait_for_connection()
simdet.wait_for_connection()


@pytest.mark.parametrize(
    "finder, reference, expected",
    [
        [
            utils.findbypv,
            f"{AD_IOC_PREFIX}image1:ArrayData",
            dict(read=["simdet.image.array_data"], write=["simdet.image.array_data"]),
        ],
        [
            utils.findbypv,
            f"{AD_IOC_PREFIX}HDF1:FilePath_RBV",
            dict(read=["simdet.hdf1.file_path"], write=[]),
        ],
        [
            utils.findbypv,
            f"{AD_IOC_PREFIX}cam1:Acquire",
            dict(read=[], write=["simdet.cam.acquire"]),
        ],
        [
            utils.findbypv,
            f"{GP_IOC_PREFIX}m1.RBV",
            dict(read=["gpm1.user_readback"], write=[]),
        ],
        [utils.findbyname, "m1_user_setpoint", None],
        [utils.findbyname, simdet.hdf1.array_size.name, "simdet.hdf1.array_size"],
        [utils.findbyname, "simdet_hdf1_array_size", "simdet.hdf1.array_size"],
        [utils.findbyname, "simdet_image_dim1_sa", "simdet.image.array_size.dim1_sa"],
        [
            utils.findbyname,
            "simdet_cam_peak_width_peak_width_y",
            "simdet.cam.peak_width.peak_width_y",
        ],
        [utils.findbyname, gpm1.user_setpoint.name, "m1.user_setpoint"],
        [utils.findbyname, simdet.cam.acquire.name, "simdet.cam.acquire"],
    ],
)
def test_main(finder, reference, expected):
    answer = finder(reference, ns=dict(m1=gpm1, simdet=simdet))
    assert answer == expected
