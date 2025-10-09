import datetime

import pytest
from ophyd.areadetector import ADComponent
from ophyd.areadetector import EpicsSignal
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
from .. import CamMixin_V34 as CamMixin
from .. import SimDetectorCam_V34
from .. import SingleTrigger_V34 as SingleTrigger
from .. import ensure_AD_plugin_primed
from ..area_detector_factory import PLUGIN_DEFAULTS
from ..area_detector_factory import ad_creator


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


@pytest.fixture()
def adsimdet():
    """EPICS ADSimDetector."""

    adsimdet = ad_creator(
        IOC_AD,
        name="adsimdet",
        class_name="MySimDet",
        plugins=[
            {"cam": {"class": SimDetectorCam_V34}},
            "image",
            "pva",
            {
                "hdf1": {
                    "class": AD_EpicsFileNameHDF5Plugin,
                    "write_path_template": WRITE_PATH_TEMPLATE,
                    "read_path_template": READ_PATH_TEMPLATE,
                }
            },
            {
                "jpeg1": {
                    "class": AD_EpicsFileNameJPEGPlugin,
                    "suffix": "JPEG1:",
                    "write_path_template": WRITE_PATH_TEMPLATE,
                    "read_path_template": READ_PATH_TEMPLATE,
                }
            },
            {
                "tiff1": {
                    "class": AD_EpicsFileNameTIFFPlugin,
                    "suffix": "TIFF1:",
                    "write_path_template": WRITE_PATH_TEMPLATE,
                    "read_path_template": READ_PATH_TEMPLATE,
                }
            },
        ],
    )

    cache = SignalSaveRestoreCache()

    adsimdet.stage_sigs["cam.wait_for_plugins"] = "Yes"
    adsimdet.wait_for_connection(timeout=15)
    for plugin_name in "hdf1 jpeg1 tiff1".split():
        adsimdet.read_attrs.append(plugin_name)
        plugin = getattr(adsimdet, plugin_name)
        ensure_AD_plugin_primed(plugin, True)

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

    class MyHDF5(HDF5Plugin):
        layout_filename = ADComponent(EpicsSignal, "XMLFileName", kind="config", string=True)
        layout_filename_valid = ADComponent(EpicsSignal, "XMLValid_RBV", kind="omitted", string=True)
        nd_attr_status = ADComponent(EpicsSignal, "NDAttributesStatus", kind="omitted", string=True)

    plugin_defaults = PLUGIN_DEFAULTS.copy()
    plugin_defaults["hdf1"].pop("read_path_template", None)
    plugin_defaults["hdf1"].pop("write_path_template", None)

    det = ad_creator(
        IOC_AD,
        name="adsingle",
        class_name="MyAdSingle",
        plugins=[
            {"cam": {"class": SimDetectorCam_V34}},
            "image",
            "pva",
            {"hdf1": {"class": MyHDF5}},  # local, custom class
        ],
        plugin_defaults=plugin_defaults,
    )

    det.wait_for_connection()

    # Configure detector (and save any previous settings).
    cache = SignalSaveRestoreCache()
    settings = {
        det.hdf1.file_path: "/tmp/test/",
        det.hdf1.file_name: det.name,
        det.hdf1.file_template: "%s%s_%3.3d.h5",
    }
    for signal, value in settings.items():
        cache.save(signal)
        signal.put(value)
    cache.save(det.hdf1.file_write_mode)
    cache.save(det.hdf1.num_capture)

    det.hdf1.kind = 3

    yield det
    det.unstage()
    cache.restore()
