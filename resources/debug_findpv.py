"""
examine the execution of utils.findbypv()

needs a connection to PVs, of course
"""

import apstools.utils
import ophyd
import ophyd.areadetector.filestore_mixins
import ophyd.areadetector.plugins
import os
import sys

sys.path.append(
    os.path.abspath(
        os.path.join(__file__, "..")
    )
)

AD_IOC_PREFIX = "adsky:"
GP_IOC_PREFIX = "sky:"
AD_IOC_FILES_ROOT = "/"
BLUESKY_FILES_ROOT = "/tmp/docker_ioc/iocad"
IOC_IMAGE_DIR = "/tmp/images/"
AD_IOC_PATH = os.path.join(
    AD_IOC_FILES_ROOT,
    IOC_IMAGE_DIR.lstrip("/")
)
BLUESKY_PATH = os.path.join(
    BLUESKY_FILES_ROOT,
    IOC_IMAGE_DIR.lstrip("/")
)


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


def main():
    gpm1 = ophyd.EpicsMotor(f"{GP_IOC_PREFIX}m1", name="gpm1")
    simdet = MyDetector(AD_IOC_PREFIX, name="simdet")
    gpm1.wait_for_connection()
    simdet.wait_for_connection()

    ns = dict(m1=gpm1, simdet=simdet)

    print(f'{apstools.utils.findbypv(f"{AD_IOC_PREFIX}image1:ArrayData", ns=ns) = }')
    print(f'{apstools.utils.findbypv(f"{AD_IOC_PREFIX}HDF1:FilePath_RBV", ns=ns) = }')
    print(f'{apstools.utils.findbypv(f"{AD_IOC_PREFIX}cam1:Acquire", ns=ns) = }')
    print(f'{apstools.utils.findbypv(f"{GP_IOC_PREFIX}m1.RBV", ns=ns) = }')

    print(f'{apstools.utils.findbyname(gpm1.user_setpoint.name, ns=ns) = }')
    print(f'{apstools.utils.findbyname("m1_user_setpoint", ns=ns) = }')
    print(f'{apstools.utils.findbyname(simdet.cam.acquire.name, ns=ns) = }')
    print(f'{apstools.utils.findbyname("simdet_hdf1_array_size", ns=ns) = }')
    print(f'{apstools.utils.findbyname("simdet_image_dim1_sa", ns=ns) = }')
    print(f'{apstools.utils.findbyname("simdet_cam_peak_width_peak_width_y", ns=ns) = }')


if __name__ == "__main__":
    main()
