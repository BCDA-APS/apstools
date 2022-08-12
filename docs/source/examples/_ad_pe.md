# Example: ADPerkinElmer Area Detector & HDF5 File Name (default)

Demonstrate the setup of an
[ADPerkinElmer](https://github.com/areaDetector/ADPerkinElmer) camera driver
(part of [EPICS area
detector](https://areadetector.github.io/master/index.html)) to acquire an image
with [bluesky](https://blueskyproject.io/) and write it to an
[HDF5](https://www.hdfgroup.org/solutions/hdf5) file.

## EPICS Area Detector IOC

***This*** Perkin-Elmer detector IOC shares its file system with the Bluesky
workstation.  Thus, the file path is the same on both the IOC
(`AD_IOC_MOUNT_PATH`) and the Bluesky (local) workstation
(`BLUESKY_MOUNT_PATH`).  Following the setup in the *File-Directories* section
of the [basic example](_ad_adsim_hdf5_basic.ipynb):

```py
import pathlib

IOC = "PE1:"  # TODO: replace with your IOC's prefix

AD_IOC_MOUNT_PATH = pathlib.Path("/local/data")  # TODO: use yours
BLUESKY_MOUNT_PATH = pathlib.Path("/local/data")  # TODO: use yours
IMAGE_DIR = "example/%Y/%m/%d"

# MUST end with a `/`, pathlib will NOT provide it
WRITE_PATH_TEMPLATE = f"{AD_IOC_MOUNT_PATH / IMAGE_DIR}/"
READ_PATH_TEMPLATE = f"{BLUESKY_MOUNT_PATH / IMAGE_DIR}/"
```

## ophyd

The **ADPerkinElmer** driver is supported by `ophyd.areadetector`'s
[PerkinElmerDetectorCam](https://blueskyproject.io/ophyd/generated/ophyd.areadetector.cam.PerkinElmerDetectorCam.html)
class.  We'll use that class here since we want to update that class for changes
in area detector's `ADCore`.

Note that ophyd makes a distinction (using the Perkin-Elmer here as an example)
between `PerkinElmerDetector` and `PerkinElmerDetectorCam`.  The
`PerkinElmerDetector` includes `PerkinElmerDetectorCam` as a component to build
a useful detector.  We must customize the `PerkinElmerDetectorCam` class with
updates, so we can't use the stock `PerkinElmerDetector`.

```py
from apstools.devices import CamMixin_V34
from ophyd.areadetector import PerkinElmerDetectorCam

class PerkinElmerDetectorCam_V34(CamMixin_V34, PerkinElmerDetectorCam):
    """Update PerkinElmerDetectorCam to ADCore 3.4+."""
```

Build a class which configures the HDF5 plugin with the data acquisition methods we need:

```py
from ophyd.areadetector.filestore_mixins import FileStoreHDF5IterativeWrite
from ophyd.areadetector.plugins import HDF5Plugin_V34 as HDF5Plugin

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
```

**NOTE**: If you want to control the HDF5 file naming with EPICS PVs (in area
detector), then replace the `MyHDF5Plugin` class with
`AD_EpicsFileNameHDF5Plugin` when creating the detector class below and follow
the additional instructions and cautions in the *HDF5:
AD_EpicsFileNameHDF5Plugin* section of the [custom HDF5 image file names
example](./_ad_adsim_hdf5_custom_names.ipynb). You'll need this import:

```py
from apstools.devices import AD_EpicsFileNameHDF5Plugin
```

Then, build the detector class which puts it all together:

```py
from apstools.devices import SingleTrigger_V34
from ophyd import ADComponent
from ophyd.areadetector import DetectorBase

class PerkinElmerDetector_V34(SingleTrigger_V34, DetectorBase):
    """
    ADSimDetector

    SingleTrigger:

    * stop any current acquisition
    * sets image_mode to 'Multiple'
    """

    cam = ADComponent(PerkinElmerDetectorCam_V34, "cam1:")
    hdf1 = ADComponent(
        MyHDF5Plugin,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )
    image = ADComponent(ImagePlugin, "image1:")
```

Create the Python object for the detector:

```py
det_pe = PerkinElmerDetector_V34(IOC, name="det_pe")
det_pe.wait_for_connection(timeout=15)

det_pe.missing_plugins()  # confirm all plugins are defined
det_pe.read_attrs.append("hdf1")  # include `hdf1` plugin with 'det_pe.read()'

# override default settings from ophyd
# Plugins will tell the camera driver when acquisition is finished.
# RunEngine will wait until `PE1:cam1:AcquireBusy_RBV` PV goes to zero.
det_pe.cam.stage_sigs["wait_for_plugins"] = "Yes"
det_pe.hdf1.stage_sigs["blocking_callbacks"] = "No"
det_pe.image.stage_sigs["blocking_callbacks"] = "No"
```

Consider staging any customizations you wish for data acquisition:

```py
# IOC may create up to 5 new subdirectories, as needed
det_pe.hdf1.create_directory.put(-5)

NUM_FRAMES = 5
det_pe.cam.stage_sigs["acquire_period"] = 0.1
det_pe.cam.stage_sigs["acquire_time"] = 0.01
det_pe.cam.stage_sigs["num_images"] = 5
det_pe.hdf1.stage_sigs["num_capture"] = 0  # capture ALL frames received
det_pe.hdf1.stage_sigs["compression"] = "zlib"  # LZ4
# det_pe.hdf1.stage_sigs["queue_size"] = 20
```

## bluesky

Use with the bluesky RunEngine `RE` like any other detector in a plan, such as:

```py
RE(bp.count([det_pe]))
```

See the *bluesky* section of the 
[basic example](_ad_adsim_hdf5_basic.ipynb) for
more information.
