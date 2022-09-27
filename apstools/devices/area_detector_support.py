"""
Area Detector Support
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~AD_EpicsFileNameHDF5Plugin
   ~AD_EpicsFileNameJPEGPlugin
   ~AD_EpicsFileNameMixin
   ~AD_EpicsFileNameTIFFPlugin
   ~AD_EpicsHdf5FileName
   ~AD_EpicsHDF5IterativeWriter
   ~AD_EpicsJPEGFileName
   ~AD_EpicsJPEGIterativeWriter
   ~AD_EpicsTIFFFileName
   ~AD_EpicsTIFFIterativeWriter
   ~AD_full_file_name_local
   ~AD_plugin_primed
   ~AD_prime_plugin
   ~AD_prime_plugin2
   ~AD_setup_FrameType
   ~CamMixin_V3_1_1
   ~CamMixin_V34
   ~SingleTrigger_V34
"""

from collections import OrderedDict
from ophyd import EpicsSignal
from ophyd import EpicsSignalRO
from ophyd import EpicsSignalWithRBV
from ophyd.areadetector import ADComponent
from ophyd.areadetector import CamBase
from ophyd.areadetector import SingleTrigger
from ophyd.areadetector.filestore_mixins import FileStoreBase
from ophyd.areadetector.filestore_mixins import FileStoreIterativeWrite
from ophyd.areadetector.filestore_mixins import FileStorePluginBase
from ophyd.areadetector.plugins import HDF5Plugin_V34 as HDF5Plugin
from ophyd.areadetector.plugins import JPEGPlugin_V34 as JPEGPlugin
from ophyd.areadetector.plugins import TIFFPlugin_V34 as TIFFPlugin
import datetime
import epics
import itertools
import logging
import numpy as np
from packaging import version
import pathlib
import time
import warnings

logger = logging.getLogger(__name__)

# fmt: off
AD_FrameType_schemes = {
    "reset": dict(  # default names from Area Detector code
        ZRST="Normal",
        ONST="Background",
        TWST="FlatField",
    ),
    "NeXus": dict(  # NeXus (typical locations)
        ZRST="/entry/data/data",
        ONST="/entry/data/dark",
        TWST="/entry/data/white",
    ),
    "DataExchange": dict(  # APS Data Exchange
        ZRST="/exchange/data",
        ONST="/exchange/data_dark",
        TWST="/exchange/data_white",
    ),
}
# fmt: on


def AD_setup_FrameType(prefix, scheme="NeXus"):
    """
    configure so frames are identified & handled by type (dark, white, or image)

    PARAMETERS

        prefix
            *str* :
            EPICS PV prefix of area detector, such as ``13SIM1:``
        scheme
            *str* :
            any key in the ``AD_FrameType_schemes`` dictionary

    This routine prepares the EPICS Area Detector to identify frames
    by image type for handling by clients, such as the HDF5 file writing plugin.
    With the HDF5 plugin, the ``FrameType`` PV is added to the NDattributes
    and then used in the layout file to direct the acquired frame to
    the chosen dataset.  The ``FrameType`` PV value provides the HDF5 address
    to be used.

    To use a different scheme than the defaults, add a new key to
    the ``AD_FrameType_schemes`` dictionary, defining storage values for the
    fields of the EPICS ``mbbo`` record that you will be using.

    see: https://nbviewer.jupyter.org/github/BCDA-APS/use_bluesky/blob/main/lessons/sandbox/images_darks_flats.ipynb

    EXAMPLE::

        AD_setup_FrameType("2bmbPG3:", scheme="DataExchange")

    * Call this function *before* creating the ophyd area detector object
    * use lower-level PyEpics interface
    """
    db = AD_FrameType_schemes.get(scheme)
    if db is None:
        raise ValueError(
            f"unknown AD_FrameType_schemes scheme: {scheme}"
            "\n Should be one of: " + ", ".join(AD_FrameType_schemes.keys())
        )

    template = "{}cam1:FrameType{}.{}"
    for field, value in db.items():
        epics.caput(template.format(prefix, "", field), value)
        epics.caput(template.format(prefix, "_RBV", field), value)


def AD_plugin_primed(plugin):
    """
    Has area detector pushed an NDarray to the file writer plugin?  True or False

    PARAMETERS

    plugin
        *obj* :
        area detector plugin to be *primed* (such as ``detector.hdf1``)

    EXAMPLE::

        AD_plugin_primed(detector.hdf1)

    Works around an observed issue: #598
    https://github.com/NSLS-II/ophyd/issues/598#issuecomment-414311372

    If detector IOC has just been started and has not yet taken an image
    with the file writer plugin, then a TimeoutError will occur as the
    file writer plugin "Capture" is set to 1 (Start).  In such case,
    first acquire at least one image with the file writer plugin enabled.

    Also issue in apstools (needs a robust method to detect if primed):
    https://github.com/BCDA-APS/apstools/issues/464

    Since Area Detector release 2.1 (2014-10-14).

    The *prime* process is not needed if you select the
    *LazyOpen* feature with *Stream* mode for the file plugin.
    *LazyOpen* defers file creation until the first frame arrives
    in the plugin. This removes the need to initialize the plugin
    with a dummy frame before starting capture.
    """
    cam = plugin.parent.cam
    tests = []

    for obj in (cam, plugin):
        test = np.array(obj.array_size.get()).sum() != 0
        tests.append(test)
        if not test:
            logger.debug("'%s' image size is zero", obj.name)

    checks = dict(
        array_size=False,
        color_mode=True,
        data_type=True,
    )
    for key, as_string in checks.items():
        c = getattr(cam, key).get(as_string=as_string)
        p = getattr(plugin, key).get(as_string=as_string)
        test = c == p
        tests.append(test)
        if not test:
            logger.debug("%s does not match", key)

    return False not in tests


def AD_prime_plugin(detector, plugin):
    """
    Prime this area detector's file writer plugin.

    PARAMETERS

    detector
        *obj* :
        area detector (such as ``detector``)
    plugin
        *obj* :
        area detector plugin to be *primed* (such as ``detector.hdf1``)

    EXAMPLE::

        AD_prime_plugin(detector, detector.hdf1)
    """
    nm = f"{plugin.parent.name}.{plugin.attr_name}"
    warnings.warn(f"Use AD_prime_plugin2({nm}) instead.")
    AD_prime_plugin2(plugin)


def AD_prime_plugin2(plugin):
    """
    Prime this area detector's file writer plugin.

    Collect and push an NDarray to the file writer plugin.
    Works with all file writer plugins.

    Based on ``ophyd.areadetector.plugins.HDF5Plugin.warmup()``.

    PARAMETERS

    plugin
        *obj* :
        area detector plugin to be *primed* (such as ``detector.hdf1``)

    EXAMPLE::

        AD_prime_plugin2(detector.hdf1)

    """
    if AD_plugin_primed(plugin):
        logger.debug("'%s' plugin is already primed", plugin.name)
        return

    sigs = OrderedDict(
        [
            (plugin.enable, 1),
            (plugin.parent.cam.array_callbacks, 1),  # set by number
            (plugin.parent.cam.image_mode, 0),  # Single, set by number
            # Trigger mode names are not identical for every camera.
            # Assume here that the first item in the list is
            # the best default choice to prime the plugin.
            (plugin.parent.cam.trigger_mode, 0),  # set by number
            # just in case the acquisition time is set very long...
            (plugin.parent.cam.acquire_time, 1),
            (plugin.parent.cam.acquire_period, 1),
            (plugin.parent.cam.acquire, 1),  # set by number
        ]
    )

    original_vals = {sig: sig.get() for sig in sigs}

    for sig, val in sigs.items():
        time.sleep(0.1)  # abundance of caution
        sig.set(val).wait()

    time.sleep(2)  # wait for acquisition

    for sig, val in reversed(list(original_vals.items())):
        time.sleep(0.1)
        sig.set(val).wait()


def AD_full_file_name_local(plugin):
    """
    Return AD plugin's *Last filename* using local filesystem path.

    Get the full name, in terms of the bluesky filesystem, for the image file
    recently-acquired by the area detector plugin.

    Return the name as a pathlib object.

    PARAMETERS

    plugin *obj* :
        Instance of ophyd area detector file writing plugin.

    (new in apstools release 1.6.2)
    """
    fname = plugin.full_file_name.get().strip()
    if fname == "":
        return None

    ffname = pathlib.Path(fname)  # FIXME: OS style?
    if plugin.read_path_template == plugin.write_path_template:
        return ffname

    # identify the common last parts of the file directories
    read_parts = pathlib.Path(plugin.read_path_template).parts
    write_parts = pathlib.Path(plugin.write_path_template).parts
    icommon = 0
    for i in range(min(len(read_parts), len(write_parts))):
        i1 = -i - 1
        if read_parts[i1:] != write_parts[i1:]:
            icommon = i
            break

    if icommon == 0:
        raise ValueError(
            "No common part to file paths. " "Cannot convert to local file path."
        )

    # fmt: off
    local_root = pathlib.Path().joinpath(*read_parts[:-icommon])
    common_parts = ffname.parts[len(write_parts[:-icommon]):]
    local_ffname = local_root.joinpath(*common_parts)
    # fmt: on

    return local_ffname


class AD_EpicsFileNameMixin(FileStorePluginBase):
    """
    Custom class to define image file name from EPICS.

    Used as part of AD_EpicsFileNameHDF5Plugin.

    .. index:: Ophyd Device Support; AD_EpicsHdf5FileName

    .. caution:: *Caveat emptor* applies here.  You assume expertise!

    Replace standard ophyd file naming algorithm (where file names
    are defined as UUID strings, virtually guaranteeing that
    no existing images files will ever be overwritten).

    Caller is responsible for setting values of these Components:

    * array_counter
    * auto_increment
    * auto_save
    * compression (only HDF)
    * create_directory
    * file_name
    * file_number
    * file_path
    * file_template
    * num_capture

    .. autosummary::

        ~make_filename
        ~get_frames_per_point
        ~stage

    To allow users to control the file **name**,
    we override the ``make_filename()`` method here
    and we need to override some intervening classes.

    To allow users to control the file **number**,
    we override the ``stage()`` method here
    and triple-comment out that line, and bring in
    sections from the methods we are replacing here.

    It is allowed to set the ``file_template="%s%s.h5"``
    so the file name does not include the file number.

    The image file name is set in ``FileStoreBase.make_filename()``
    from ``ophyd.areadetector.filestore_mixins``.  This is called
    (during device staging) from ``FileStoreBase.stage()``
    """

    def _remove_caller_stage_sigs(self):
        """Caller is responsible for setting these stage_sigs."""
        caller_sets_these = """
        array_counter
        auto_increment
        auto_save
        compression (only HDF)
        create_directory
        file_name
        file_number
        file_path
        file_template
        num_capture
        """.split()
        for key in caller_sets_these:
            if key in self.stage_sigs:
                self.stage_sigs.pop(key)

    def make_filename(self):
        """
        overrides default behavior: Get info from EPICS file writer plugin.
        """
        # start of the file name, file number will be appended per template
        filename = self.file_name.get()
        file_path = self.file_path.get()
        formatter = datetime.datetime.now().strftime

        # Directory (used by IOC) for file writer plugin to write the file.
        write_path = formatter(file_path)

        # Directory (used by bluesky) for databroker to read the file.
        read_path = formatter(self.read_path_template)

        return filename, read_path, write_path

    def get_frames_per_point(self):
        """overrides default behavior"""
        return self.num_capture.get()

    def stage(self):
        """
        Overrides default behavior of parent class.

        Parent class items overridden here:

        * Sets file_name based on a UUID.
        * Sets file_path from write_path_template.
        * Sets file_number to 0.

        Set EPICS items before device is staged, then copy EPICS
        naming template (and other items) to ophyd after staging.
        """
        if "capture" in self.stage_sigs:
            self.stage_sigs.move_to_end("capture", last=True)

        # Get the file name and paths from EPICS.
        filename, read_path, write_path = self.make_filename()

        # Ensure we do not have an old file open.
        self.capture.set(0).wait()

        # Set these before capture is turned on.
        # They will not be reset on 'unstage' anyway.
        self.file_path.set(write_path).wait()
        self.file_name.set(filename).wait()

        # Get file number now, it is incremented during stage().
        file_number = self.file_number.get()

        # Call ancestor's stage(), skipping parent's stage().
        FileStoreBase.stage(self)

        # AD applies the file name templating in C.
        # We can't access that result until after acquisition
        # so we apply the same template here in Python.
        template = self.file_template.get(use_monitor=False)
        try:
            # assume template includes format for a file number
            self._fn = template % (read_path, filename, file_number)
        except (TypeError, ValueError):
            # in case template does not include file_number
            self._fn = template % (read_path, filename)
        self._fp = read_path
        if not self.file_path_exists.get():
            raise IOError(f"Path '{self.file_path.get()}' does not exist on IOC.")

        # index each image frame (used in generate_datum() method)
        self._point_counter = itertools.count()

        # from FileStoreHDF5.stage()
        res_kwargs = {"frame_per_point": self.get_frames_per_point()}
        self._generate_resource(res_kwargs)


class AD_EpicsHdf5FileName(AD_EpicsFileNameMixin):
    """
    Custom class to define HDF5 image file name from EPICS PVs.

    Used as part of AD_EpicsFileNameHDF5Plugin.
    """

    def __init__(self, *args, **kwargs):
        FileStorePluginBase.__init__(self, *args, **kwargs)
        self.filestore_spec = "AD_HDF5"  # spec name stored in resource doc
        self.stage_sigs.update(
            [
                ("file_write_mode", "Stream"),
                ("capture", 1),
            ]
        )
        self._remove_caller_stage_sigs()
        # "capture" must always come last
        self.stage_sigs["capture"] = self.stage_sigs.pop("capture")


class AD_EpicsHDF5IterativeWriter(AD_EpicsHdf5FileName, FileStoreIterativeWrite):
    """
    intermediate class between AD_EpicsHdf5FileName and AD_EpicsFileNameHDF5Plugin

    (new in apstools release 1.6.2)
    """

    pass


class AD_EpicsFileNameHDF5Plugin(HDF5Plugin, AD_EpicsHDF5IterativeWriter):
    """
    Alternative to HDF5Plugin: EPICS area detector PV sets file name.

    .. index:: Ophyd Device Support; AD_EpicsFileNameHDF5Plugin

    .. caution:: *Caveat emptor* applies here.  You assume expertise!

    Uses ``AD_EpicsHdf5FileName``.

    EXAMPLE::

        from apstools.devices.area_detector_support import AD_EpicsFileNameHDF5Plugin
        from ophyd import EpicsSignalWithRBV
        from ophyd.areadetector import ADComponent
        from ophyd.areadetector import DetectorBase
        from ophyd.areadetector import SingleTrigger
        from ophyd.areadetector.plugins import ImagePlugin_V34 as ImagePlugin
        from ophyd.areadetector.plugins import PvaPlugin_V34 as PvaPlugin
        from ophyd.areadetector import SimDetectorCam
        import datetime
        import pathlib


        IOC = "ad:"
        IMAGE_DIR = "adsimdet/%Y/%m/%d"
        AD_IOC_MOUNT_PATH = pathlib.Path("/tmp")
        BLUESKY_MOUNT_PATH = pathlib.Path("/tmp/docker_ioc/iocad/tmp")

        # MUST end with a `/`, pathlib will NOT provide it
        WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"
        READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / IMAGE_DIR}/"


        class MyFixedCam(SimDetectorCam):
            pool_max_buffers = None
            offset = ADComponent(EpicsSignalWithRBV, "Offset")


        class MySimDetector(SingleTrigger, DetectorBase):
            '''ADSimDetector'''

            cam = ADComponent(MyFixedCam, "cam1:")
            image = ADComponent(ImagePlugin, "image1:")
            hdf1 = ADComponent(
                AD_EpicsFileNameHDF5Plugin,
                "HDF1:",
                write_path_template=WRITE_PATH_TEMPLATE,
                read_path_template=READ_PATH_TEMPLATE,
            )
            pva = ADComponent(PvaPlugin, "Pva1:")

    (new in apstools release 1.6.2)
    """

    pass


class AD_EpicsJPEGFileName(AD_EpicsFileNameMixin):
    """
    Custom class to define JPEG image file name from EPICS PVs.

    Used as part of AD_EpicsFileNameJPEGPlugin.
    """

    def __init__(self, *args, **kwargs):
        FileStorePluginBase.__init__(self, *args, **kwargs)
        self.filestore_spec = "AD_JPEG"  # spec name stored in resource doc
        self.stage_sigs.update(
            [
                ("file_write_mode", "Stream"),
                ("capture", 1),
            ]
        )
        self._remove_caller_stage_sigs()
        # "capture" must always come last
        self.stage_sigs["capture"] = self.stage_sigs.pop("capture")


class AD_EpicsJPEGIterativeWriter(AD_EpicsJPEGFileName, FileStoreIterativeWrite):
    """
    intermediate class between AD_EpicsJPEGFileName and AD_EpicsFileNameJPEGPlugin

    (new in apstools release 1.6.2)
    """

    pass


class AD_EpicsFileNameJPEGPlugin(JPEGPlugin, AD_EpicsJPEGIterativeWriter):
    """
    Alternative to JPEGPlugin: EPICS area detector PV sets file name.

    .. index:: Ophyd Device Support; AD_EpicsFileNameJPEGPlugin

    .. caution:: *Caveat emptor* applies here.  You assume expertise!

    Uses ``AD_EpicsJpegFileName``.

    EXAMPLE::

        from apstools.devices.area_detector_support import AD_EpicsFileNameJPEGPlugin
        from ophyd import EpicsSignalWithRBV
        from ophyd.areadetector import ADComponent
        from ophyd.areadetector import DetectorBase
        from ophyd.areadetector import SingleTrigger
        from ophyd.areadetector.plugins import ImagePlugin_V34 as ImagePlugin
        from ophyd.areadetector.plugins import PvaPlugin_V34 as PvaPlugin
        from ophyd.areadetector import SimDetectorCam
        import datetime
        import pathlib


        IOC = "ad:"
        IMAGE_DIR = "adsimdet/%Y/%m/%d"
        AD_IOC_MOUNT_PATH = pathlib.Path("/tmp")
        BLUESKY_MOUNT_PATH = pathlib.Path("/tmp/docker_ioc/iocad/tmp")

        # MUST end with a `/`, pathlib will NOT provide it
        WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"
        READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / IMAGE_DIR}/"


        class MyFixedCam(SimDetectorCam):
            pool_max_buffers = None
            offset = ADComponent(EpicsSignalWithRBV, "Offset")


        class MySimDetector(SingleTrigger, DetectorBase):
            '''ADSimDetector'''

            cam = ADComponent(MyFixedCam, "cam1:")
            image = ADComponent(ImagePlugin, "image1:")
            jpeg1 = ADComponent(
                AD_EpicsFileNameHDF5Plugin,
                "JPEG1:",
                write_path_template=WRITE_PATH_TEMPLATE,
                read_path_template=READ_PATH_TEMPLATE,
            )
            pva = ADComponent(PvaPlugin, "Pva1:")

    (new in apstools release 1.6.2)
    """

    pass


class AD_EpicsTIFFFileName(AD_EpicsFileNameMixin):
    """
    Custom class to define TIFF image file name from EPICS PVs.

    Used as part of AD_EpicsFileNameTIFFPlugin.
    """

    def __init__(self, *args, **kwargs):
        FileStorePluginBase.__init__(self, *args, **kwargs)
        self.filestore_spec = "AD_TIFF"  # spec name stored in resource doc
        self.stage_sigs.update(
            [
                ("file_write_mode", "Stream"),
                ("capture", 1),
            ]
        )
        self._remove_caller_stage_sigs()
        # "capture" must always come last
        self.stage_sigs["capture"] = self.stage_sigs.pop("capture")


class AD_EpicsTIFFIterativeWriter(AD_EpicsTIFFFileName, FileStoreIterativeWrite):
    """
    intermediate class between AD_EpicsTIFFFileName and AD_EpicsFileNameTIFFPlugin

    (new in apstools release 1.6.2)
    """

    pass


class AD_EpicsFileNameTIFFPlugin(TIFFPlugin, AD_EpicsTIFFIterativeWriter):
    """
    Alternative to TIFFPlugin: EPICS area detector PV sets file name.

    .. index:: Ophyd Device Support; AD_EpicsFileNameTIFFPlugin

    .. caution:: *Caveat emptor* applies here.  You assume expertise!

    Uses ``AD_EpicsTIFFFileName``.

    EXAMPLE::

        from apstools.devices.area_detector_support import AD_EpicsFileNameTIFFPlugin
        from ophyd import EpicsSignalWithRBV
        from ophyd.areadetector import ADComponent
        from ophyd.areadetector import DetectorBase
        from ophyd.areadetector import SingleTrigger
        from ophyd.areadetector.plugins import ImagePlugin_V34 as ImagePlugin
        from ophyd.areadetector.plugins import PvaPlugin_V34 as PvaPlugin
        from ophyd.areadetector import SimDetectorCam
        import datetime
        import pathlib


        IOC = "ad:"
        IMAGE_DIR = "adsimdet/%Y/%m/%d"
        AD_IOC_MOUNT_PATH = pathlib.Path("/tmp")
        BLUESKY_MOUNT_PATH = pathlib.Path("/tmp/docker_ioc/iocad/tmp")

        # MUST end with a `/`, pathlib will NOT provide it
        WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"
        READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / IMAGE_DIR}/"


        class MyFixedCam(SimDetectorCam):
            pool_max_buffers = None
            offset = ADComponent(EpicsSignalWithRBV, "Offset")


        class MySimDetector(SingleTrigger, DetectorBase):
            '''ADSimDetector'''

            cam = ADComponent(MyFixedCam, "cam1:")
            image = ADComponent(ImagePlugin, "image1:")
            tiff1 = ADComponent(
                AD_EpicsFileNameTIFFPlugin,
                "TIFF1:",
                write_path_template=WRITE_PATH_TEMPLATE,
                read_path_template=READ_PATH_TEMPLATE,
            )
            pva = ADComponent(PvaPlugin, "Pva1:")

    (new in apstools release 1.6.2)
    """

    pass


class CamMixin_V3_1_1(CamBase):
    """
    Update cam support to AD release 3.1.1.

    (new in release 1.6.3)
    """

    _cam_release = "3.1.1"
    pool_max_buffers = None
    acquire_busy = ADComponent(EpicsSignalRO, "AcquireBusy")
    offset = ADComponent(EpicsSignalWithRBV, "Offset")
    wait_for_plugins = ADComponent(EpicsSignal, "WaitForPlugins")

    @property
    def is_busy(self):
        signal = self.acquire_busy
        return signal.get() in (1, signal.enum_strs[1])


class CamMixin_V34(CamMixin_V3_1_1):
    """
    Update cam support to AD release 3.1.1.

    (new in release 1.6.3)
    """

    _cam_release = "3.4"


class SingleTrigger_V34(SingleTrigger):
    """
    Variation of ophyd's SingleTrigger mixin supporting AcquireBusy.

    (new in release 1.6.3)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        has_v34_cam_features = (
            hasattr(self, "cam")
            and hasattr(self.cam, "_cam_release")
            and version.parse(self.cam._cam_release) >= version.parse("3.4")
        )
        if has_v34_cam_features:
            self._acquisition_busy_signal = self.cam.acquire_busy
        else:
            # backwards compatibility
            self._acquisition_busy_signal = self._acquisition_signal

    def stage(self):
        """Prepare device settings before data acquisition."""
        self._acquisition_busy_signal.subscribe(self._acquire_changed)
        super(SingleTrigger, self).stage()  # from grandparent

    def unstage(self):
        """Restore device settings after data acquisition."""
        super(SingleTrigger, self).unstage()  # from grandparent
        self._acquisition_busy_signal.clear_sub(self._acquire_changed)

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
