from ..area_detector_support import AD_EpicsHdf5FileName
from bluesky import plans as bp
from bluesky import RunEngine
from ophyd.areadetector import ADComponent, SimDetectorCam
from ophyd.areadetector import SimDetector, SingleTrigger
from ophyd.areadetector.filestore_mixins import FileStoreIterativeWrite
from ophyd.areadetector.plugins import HDF5Plugin_V34 as HDF5Plugin
from ophyd.areadetector.plugins import ImagePlugin_V34 as ImagePlugin
import databroker
import pathlib


IOC = "ad:"
IMAGE_DIR = "images"
AD_IOC_MOUNT_PATH = pathlib.Path("/tmp")
BLUESKY_MOUNT_PATH = pathlib.Path(
    f"/tmp/docker_ioc/ioc{IOC.rstrip(':')}{AD_IOC_MOUNT_PATH}"
)

# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / IMAGE_DIR}/"


class myHdf5EpicsIterativeWriter(AD_EpicsHdf5FileName, FileStoreIterativeWrite):
    """Build a custom iterative writer using the override."""

    pass


class myHDF5FileNames(HDF5Plugin, myHdf5EpicsIterativeWriter):
    """Make a custom HDF5 plugin using the override."""

    pass


# define support for the detector (ADSimDetector here):
class MySimDetector(SingleTrigger, SimDetector):
    """SimDetector with HDF5 file names specified by EPICS."""

    _default_read_attrs = ["hdf1"]

    cam = ADComponent(SimDetectorCam, "cam1:")
    image = ADComponent(ImagePlugin, "image1:")

    hdf1 = ADComponent(
        myHDF5FileNames,
        suffix="HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )


def test_no_unexpected_key_in_datum_kwarg():
    """
    Test that this exception is fixed:

    TypeError: __call__() got an unexpected keyword argument 'HDF5_file_name'
    """
    cat = databroker.temp().v2
    RE = RunEngine({})
    RE.subscribe(cat.v1.insert)

    camera = MySimDetector(IOC, name="camera")
    assert isinstance(camera, MySimDetector)

    if hasattr(camera.hdf1.stage_sigs, "array_counter"):
        # remove this so array counter is not set to zero each staging
        del camera.hdf1.stage_sigs["array_counter"]

    camera.cam.stage_sigs["num_images"] = 1
    camera.hdf1.stage_sigs["num_capture"] = 1
    camera.hdf1.stage_sigs["file_template"] = "%s%s_%3.3d.h5"
    camera.hdf1.stage_sigs["compression"] = "zlib"

    # ensure the capture is always staged last
    camera.hdf1.stage_sigs["capture"] = camera.hdf1.stage_sigs.pop("capture")

    camera.wait_for_connection()
    assert camera.connected

    camera.hdf1.warmup()

    file_name = "test_image"
    file_number = camera.hdf1.file_number.get()
    file_path = AD_IOC_MOUNT_PATH / IMAGE_DIR
    file_template = "%s%s_%4.4d.h5"

    camera.hdf1.create_directory.put(-5)
    camera.hdf1.file_name.put(file_name)
    camera.hdf1.file_path.put(str(file_path))
    camera.hdf1.stage_sigs["file_template"] = file_template

    file_name = camera.hdf1.file_name.get()

    # take the image
    uids = RE(bp.count([camera], num=1))
    assert len(uids) == 1

    uid = uids[0]
    assert isinstance(uid, str)

    # Can bluesky see the new image file?
    ioc_file_name = (file_template % (file_path, "/" + file_name, file_number))
    assert camera.hdf1.full_file_name.get() == ioc_file_name

    ioc_tmp = pathlib.Path(BLUESKY_MOUNT_PATH).parent
    assert ioc_tmp.exists(), ioc_tmp

    # get the full file name in terms of the bluesky file directory
    _n = len(str(AD_IOC_MOUNT_PATH.parent))
    resource_file_name = ioc_file_name[_n:]
    image_file = ioc_tmp / resource_file_name.lstrip("/")
    assert image_file.exists(), (
        f"ioc_tmp={ioc_tmp}"
        f" resource_file_name={resource_file_name}"
        f" image_file={image_file}"
    )

    # verify that the problem key in datum_kwargs is not found
    for uid in uids:
        uid_start = None
        uid_resource = None
        id_datum = None
        for doc_type, doc in cat.v1[uid].documents():
            if doc_type == "start":
                uid_start = doc["uid"]

            elif doc_type == "datum":
                id_datum = f"{uid_resource}/0"
                assert doc["_name"] == "Datum", doc
                assert doc["datum_id"] == id_datum, doc
                # "HDF5_file_name" is an unexpected key in datum_kwargs
                assert doc["datum_kwargs"] == {"point_number": 0}, doc
                assert doc["resource"] == uid_resource, doc

            elif doc_type == "resource":
                uid_resource = doc["uid"]
                assert doc["path_semantics"] == "posix", doc
                assert doc["resource_kwargs"] == {"frame_per_point": 1}, doc
                assert doc["resource_path"] == ioc_file_name.lstrip("/"), doc
                assert doc["root"] == "/", doc
                assert doc["run_start"] == uid_start, doc
                assert doc["spec"] == "AD_HDF5", doc

    run = cat.v2[uid]
    assert run is not None

    primary = run.primary
    rsrc = primary._resources
    assert isinstance(rsrc, list), rsrc
    assert len(rsrc) == 1
    rsrc = rsrc[0].to_dict()
    assert isinstance(rsrc, dict), rsrc
    assert rsrc["path_semantics"] == "posix", rsrc
    assert rsrc["resource_kwargs"] == {"frame_per_point": 1}, rsrc
    assert rsrc["resource_path"] == ioc_file_name.lstrip("/"), rsrc
    assert rsrc["root"] == "/", rsrc
    assert rsrc["run_start"] == uid_start, rsrc
    assert rsrc["spec"] == "AD_HDF5", rsrc
    assert rsrc["uid"] == uid_resource, rsrc

    # If this errors, that's issue 651:
    ds = run.primary.read()
    assert ds is not None
    assert camera.image.name in ds
