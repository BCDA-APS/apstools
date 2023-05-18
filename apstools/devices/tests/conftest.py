import datetime

import pytest
from ophyd.areadetector import ADComponent
from ophyd.areadetector import DetectorBase
from ophyd.areadetector import EpicsSignal
from ophyd.areadetector import EpicsSignalRO
from ophyd.areadetector import SimDetectorCam
from ophyd.areadetector.plugins import HDF5Plugin_V34 as HDF5Plugin
from ophyd.areadetector.plugins import ImagePlugin_V34 as ImagePlugin
from ophyd.areadetector.plugins import PvaPlugin_V34 as PvaPlugin

from ...tests import IOC_AD
from ...tests import READ_PATH_TEMPLATE
from ...tests import WRITE_PATH_TEMPLATE
from ...tests import SignalSaveRestoreCache
from .. import AD_EpicsFileNameHDF5Plugin
from .. import AD_EpicsFileNameJPEGPlugin
from .. import AD_EpicsFileNameTIFFPlugin
from .. import AD_plugin_primed
from .. import AD_prime_plugin2
from .. import CamMixin_V34 as CamMixin
from .. import SingleTrigger_V34 as SingleTrigger


def pytest_addoption(parser):
    parser.addoption("--run-local", action="store_true", default=False, help="run local tests")


def pytest_configure(config):
    config.addinivalue_line("markers", "local: mark test to run locally")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--run-local"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_local = pytest.mark.skip(reason="need --run-local option to run")
    for item in items:
        if "local" in item.keywords:
            item.add_marker(skip_local)


@pytest.fixture()
def fname():
    "File (base) name."
    dt = datetime.datetime.now()
    fname = f"test-image-{dt.minute:02d}-{dt.second:02d}"
    yield fname


class MySimDetectorCam(CamMixin, SimDetectorCam):
    """triggering configuration and AcquireBusy support"""


class MySimDetector(SingleTrigger, DetectorBase):
    """ADSimDetector"""

    cam = ADComponent(MySimDetectorCam, "cam1:")
    hdf1 = ADComponent(
        AD_EpicsFileNameHDF5Plugin,
        "HDF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )
    image = ADComponent(ImagePlugin, "image1:")
    jpeg1 = ADComponent(
        AD_EpicsFileNameJPEGPlugin,
        "JPEG1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )
    pva = ADComponent(PvaPlugin, "Pva1:")
    tiff1 = ADComponent(
        AD_EpicsFileNameTIFFPlugin,
        "TIFF1:",
        write_path_template=WRITE_PATH_TEMPLATE,
        read_path_template=READ_PATH_TEMPLATE,
    )


@pytest.fixture()
def adsimdet():
    "EPICS ADSimDetector."
    adsimdet = MySimDetector(IOC_AD, name="adsimdet")
    cache = SignalSaveRestoreCache()

    adsimdet.stage_sigs["cam.wait_for_plugins"] = "Yes"
    adsimdet.wait_for_connection(timeout=15)
    for plugin_name in "hdf1 jpeg1 tiff1".split():
        adsimdet.read_attrs.append(plugin_name)
        plugin = getattr(adsimdet, plugin_name)
        if not AD_plugin_primed(plugin):
            AD_prime_plugin2(plugin)

        # these settings are the caller's responsibility
        ext = dict(hdf1="h5", jpeg1="jpg", tiff1="tif")[plugin_name]
        settings = [
            [plugin.file_name, ""],  # control this in tests
            [plugin.create_directory, -5],
            [plugin.file_path, f"{plugin.write_path_template}/"],
            [plugin.file_template, f"%s%s_%4.4d.{ext}"],
            [plugin.auto_increment, "Yes"],
            [plugin.auto_save, "Yes"],
        ]
        if plugin_name == "hdf1":
            settings.append([plugin.compression, "zlib"])
            settings.append([plugin.zlevel, 6])
        elif plugin_name == "jpeg":
            settings.append([plugin.jpeg_quality, 50])

        for signal, value in settings:
            cache.save(signal)
            signal.put(value)
        cache.save(plugin.file_write_mode)
        cache.save(plugin.num_capture)

        if "capture" in plugin.stage_sigs:
            plugin.stage_sigs.move_to_end("capture", last=True)

    yield adsimdet

    adsimdet.unstage()
    cache.restore()


@pytest.fixture()
def adsingle():
    """Using mostly ophyd sources."""

    class MyCam(CamMixin, SimDetectorCam):
        nd_attr_status = ADComponent(EpicsSignalRO, "NDAttributesStatus", kind="omitted", string=True)

    class MyHDF5(HDF5Plugin):
        layout_filename = ADComponent(EpicsSignal, "XMLFileName", kind="config", string=True)
        layout_filename_valid = ADComponent(EpicsSignal, "XMLValid_RBV", kind="omitted", string=True)
        nd_attr_status = ADComponent(EpicsSignal, "NDAttributesStatus", kind="omitted", string=True)

    class MyAdSingle(SingleTrigger, DetectorBase):
        cam = ADComponent(MyCam, suffix="cam1:")
        hdf1 = ADComponent(MyHDF5, suffix="HDF1:")
        image = ADComponent(ImagePlugin, suffix="image1:")
        pva1 = ADComponent(PvaPlugin, suffix="Pva1:")

    det = MyAdSingle(IOC_AD, name="det")
    det.wait_for_connection()

    cache = SignalSaveRestoreCache()
    cache.save(det.hdf1.file_write_mode)
    cache.save(det.hdf1.num_capture)

    yield det
    det.unstage()
    cache.restore()
