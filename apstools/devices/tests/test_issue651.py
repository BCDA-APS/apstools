from ..area_detector_support import AD_EpicsHdf5FileName
from ..area_detector_support import AD_plugin_primed
from ..area_detector_support import AD_prime_plugin2
from bluesky import plans as bp
from bluesky import RunEngine
from ophyd.areadetector import ADComponent, SimDetectorCam
from ophyd.areadetector import SimDetector, SingleTrigger
from ophyd.areadetector.filestore_mixins import FileStoreIterativeWrite
from ophyd.areadetector.plugins import HDF5Plugin_V34 as HDF5Plugin
from ophyd.areadetector.plugins import ImagePlugin_V34 as ImagePlugin
import databroker
import h5py
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

    if not AD_plugin_primed(camera.hdf1):
        # camera.hdf1.warmup()
        AD_prime_plugin2(camera.hdf1)

    file_name = "test_image"
    file_path = AD_IOC_MOUNT_PATH / IMAGE_DIR
    file_template = "%s%s_%4.4d.h5"

    camera.hdf1.create_directory.put(-5)
    camera.hdf1.file_name.put(file_name)
    camera.hdf1.file_path.put(str(file_path))
    camera.hdf1.stage_sigs["file_template"] = file_template

    file_name = camera.hdf1.file_name.get()

    camera.stage()
    _fn, _rp, _wp = camera.hdf1.make_filename()
    assert _fn == file_name
    assert _rp == str(BLUESKY_MOUNT_PATH / IMAGE_DIR) + "/"
    assert _wp == str(AD_IOC_MOUNT_PATH / IMAGE_DIR) + "/"
    assert _rp == READ_PATH_TEMPLATE
    assert _wp == WRITE_PATH_TEMPLATE
    assert _rp == camera.hdf1.read_path_template
    assert _wp == camera.hdf1.write_path_template + "/"
    camera.unstage()
    # assert False, "diagnostic stop"

    # take the image
    file_number = camera.hdf1.file_number.get()
    uids = RE(bp.count([camera], num=1))
    assert len(uids) == 1

    uid = uids[0]
    assert isinstance(uid, str)

    # Can bluesky see the new image file?
    ioc_file_name = (file_template % (file_path, "/" + file_name, file_number))
    assert camera.hdf1.full_file_name.get() == ioc_file_name

    assert str(BLUESKY_MOUNT_PATH).startswith("/tmp/docker_ioc/")
    assert BLUESKY_MOUNT_PATH.exists(), BLUESKY_MOUNT_PATH

    # get the full file name relative to the bluesky file directory
    _n = len(camera.hdf1._root.as_posix())
    resource_path = ioc_file_name[_n:].lstrip("/")
    image_file = BLUESKY_MOUNT_PATH.parent / resource_path
    assert image_file.exists(), (
        f"BLUESKY_MOUNT_PATH={BLUESKY_MOUNT_PATH}"
        f" resource_path={resource_path}"
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
                assert doc["datum_id"] == id_datum, doc
                # "HDF5_file_name" is an unexpected key in datum_kwargs
                assert doc["datum_kwargs"] == {"point_number": 0}, doc
                assert doc["resource"] == uid_resource, doc

            elif doc_type == "resource":
                uid_resource = doc["uid"]
                assert doc["path_semantics"] == "posix", doc
                assert doc["resource_kwargs"] == {"frame_per_point": 1}, doc
                # full file name is found by databroker at f"{root}/{resource_path}"
                # root: relocatable part where databroker catalog is installed now
                # resource_path: persistent path to file
                assert doc["root"] == camera.hdf1._root.as_posix(), doc
                assert doc["resource_path"].endswith(resource_path)
                _r = str(image_file).lstrip(doc["root"]).lstrip("/")
                assert doc["resource_path"] == _r
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
    _r = str(image_file).lstrip(rsrc["root"]).lstrip("/")
    assert rsrc["resource_path"] == _r, rsrc
    assert rsrc["root"] == camera.hdf1._root.as_posix(), rsrc
    assert rsrc["run_start"] == uid_start, rsrc
    assert rsrc["spec"] == "AD_HDF5", rsrc
    assert rsrc["uid"] == uid_resource, rsrc

    # Could databroker find this file?
    image_file = BLUESKY_MOUNT_PATH.parent / resource_path
    # How WE can find it.
    assert image_file.exists()
    # How databroker finds it.
    assert (pathlib.Path(rsrc["root"]) / rsrc["resource_path"]).exists(), rsrc

    # Could databroker read this image?
    with h5py.File(str(image_file), "r") as h5:
        key = "/entry/data/data"
        assert key in h5
        data = h5[key]
        assert data is not None
        assert data.shape == (1, 1024, 1024)

    # If this errors, one cause is issue 651:
    ds = run.primary.read()
    assert ds is not None
    assert camera.image.name in ds
