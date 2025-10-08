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


# --- Intake YAML monitor for devices tests ----------------------------------
# Autouse fixture to detect tests that remove/move the unpacked databroker
# intake YAML files during the devices test run. When a test causes a
# previously-present databroker_unpack_*.yml to be missing (or listing
# errors occur), this prints diagnostics (cwd, env, search paths, file
# stats) to stderr so we can identify the offending test.
import sys
import os
import glob
import time
import traceback
from pprint import pformat


def _get_intake_search_paths():
    try:
        import databroker
        return list(databroker.catalog_search_path())
    except Exception:
        try:
            import intake
            return list(intake.catalog_search_path())
        except Exception:
            return []


def _snapshot():
    snap = {}
    snap["time"] = time.time()
    snap["cwd"] = os.getcwd()
    snap["env"] = {
        "HOME": os.environ.get("HOME"),
        "CONDA_PREFIX": os.environ.get("CONDA_PREFIX"),
        "XDG_DATA_HOME": os.environ.get("XDG_DATA_HOME"),
    }
    sp = _get_intake_search_paths()
    snap["search_path"] = sp
    files = {}
    for p in sp:
        if not p:
            continue
        files[p] = []
        try:
            for y in glob.glob(os.path.join(p, "databroker_unpack_*.yml")):
                try:
                    st = os.stat(y)
                    files[p].append({"path": y, "size": st.st_size, "mtime": st.st_mtime})
                except FileNotFoundError:
                    files[p].append({"path": y, "missing": True})
        except Exception as e:
            files[p].append({"error": f"{type(e).__name__}: {e}"})
    snap["files"] = files
    return snap


def _compare_snapshots(before, after):
    diffs = {}
    missing = []
    listing_errors = {}
    diffs["cwd_changed"] = before.get("cwd") != after.get("cwd")
    env_before = before.get("env", {})
    env_after = after.get("env", {})
    env_changes = {k: (env_before.get(k), env_after.get(k)) for k in env_before if env_before.get(k) != env_after.get(k)}
    diffs["env_changed"] = env_changes
    for p, entries in before.get("files", {}).items():
        after_entries = after.get("files", {}).get(p, [])
        after_paths = {e.get("path") for e in after_entries if "path" in e}
        for e in after_entries:
            if "error" in e:
                listing_errors[p] = e["error"]
        for e in entries:
            if "path" in e:
                if e["path"] not in after_paths:
                    missing.append({"path": e["path"], "search_dir": p, "before": e})
            elif "error" in e:
                listing_errors[p] = e["error"]
    diffs["missing_files"] = missing
    diffs["listing_errors"] = listing_errors
    return diffs


import pytest


@pytest.fixture(autouse=True)
def monitor_intake_yaml(request):
    nodeid = getattr(request.node, "nodeid", "<unknown>")
    before = _snapshot()
    yield
    try:
        after = _snapshot()
        diffs = _compare_snapshots(before, after)
        if diffs.get("missing_files") or diffs.get("listing_errors") or diffs.get("cwd_changed") or diffs.get("env_changed"):
            banner = "=" * 80
            print("\n" + banner, file=sys.stderr)
            print(f"INTAKE YAML MONITOR: test nodeid: {nodeid}", file=sys.stderr)
            print(f"Time before test: {time.ctime(before.get('time'))}", file=sys.stderr)
            print(f"Time after  test: {time.ctime(after.get('time'))}", file=sys.stderr)
            print("\n-- before snapshot --", file=sys.stderr)
            print(pformat(before), file=sys.stderr)
            print("\n-- after snapshot --", file=sys.stderr)
            print(pformat(after), file=sys.stderr)
            print("\n-- detected differences --", file=sys.stderr)
            print(pformat(diffs), file=sys.stderr)
            print("\nIf a YAML present before the test is missing after the test, that test likely\nremoved/moved the file or changed working directories in a way that\nbroke Intake's path resolution. Inspect the test above in the CI log.\n", file=sys.stderr)
            print(banner + "\n", file=sys.stderr)
    except Exception:
        print("INTAKE YAML MONITOR: error while taking post-test snapshot for nodeid:", nodeid, file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

# ---------------------------------------------------------------------------
