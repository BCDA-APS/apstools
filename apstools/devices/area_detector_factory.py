"""
Area Detector Factory
+++++++++++++++++++++

.. autosummary::

   ~ad_creator
   ~ad_class_factory
   ~PLUGIN_DEFAULTS

EXAMPLES

Just the camera plugin (uses CamBase, the most basic features)::

    from apstools.devices import ad_creator
    det = ad_creator("ad:", name="det", class_name="MySimpleAD", ["cam",])

View ADSimDetector image with CA and PVA::

    from ophyd.areadetector import SimDetectorCam
    from apstools.devices import ad_creator

    det = ad_creator(
        "ad:", name="det", class_name="MySimDetector",
        [
            {"cam": {"class": SimDetectorCam}},
            "image",
            "pva",
        ],
    )

Record HDF5 images with Eiger detector. Here, both the Eiger detector IOC and
the Bluesky databroker use the same filesystem mount ``/``::

    from ophyd.areadetector import EigerDetectorCam
    from apstools.devices import ad_creator

    det = ad_creator(
        "ad:", name="det", class_name"MyEiger",
        [
            {"cam": {"class": EigerDetectorCam}},
            "image",
            {"hdf1": {"write_path_template": "/"}},
        ],
    )

Override one of the default plugin configurations.  In this case, remove the
``write_path_template`` and ``read_path_template`` keys from the ``hdf1`` plugin
support::

    from ophyd.areadetector import EigerDetectorCam
    from apstools.devices import ad_creator, PLUGIN_DEFAULTS

    plugin_defaults = PLUGIN_DEFAULTS.copy()
    plugin_defaults["hdf1"].pop("read_path_template", None)
    plugin_defaults["hdf1"].pop("write_path_template", None)

    det = ad_creator(
        "ad:", name="det", class_name"MyEiger",
        [
            {"cam": {"class": EigerDetectorCam}},
            "image",
            "hdf1",
        ],
        plugin_defaults=plugin_defaults,
    )
"""

import logging
import uuid

logger = logging.getLogger(__name__)

import ophyd.areadetector.plugins
from ophyd import ADComponent

from .area_detector_support import AD_EpicsFileNameJPEGPlugin
from .area_detector_support import AD_EpicsFileNameTIFFPlugin
from .area_detector_support import HDF5FileWriterPlugin
from .area_detector_support import SingleTrigger_V34

PLUGIN_DEFAULTS = {  # some of the common plugins
    # gets image from the detector
    "cam": {
        "suffix": "cam1:",
        "class": ophyd.areadetector.CamBase,
    },
    # for imaging
    "image": {
        "suffix": "image1:",
        "class": ophyd.areadetector.plugins.ImagePlugin_V34,
    },
    "pva": {
        "suffix": "Pva1:",
        "class": ophyd.areadetector.plugins.PvaPlugin_V34,
    },
    # signal handling
    "attr1": {
        "suffix": "Attr1:",
        "class": ophyd.areadetector.plugins.AttrPlotPlugin_V34,
    },
    "cb1": {
        "suffix": "CB1:",
        "class": ophyd.areadetector.plugins.CircularBuffPlugin_V34,
    },
    "cc1": {
        "suffix": "CC1:",
        "class": ophyd.areadetector.plugins.ColorConvPlugin_V34,
    },
    "cc2": {
        "suffix": "CC2:",
        "class": ophyd.areadetector.plugins.ColorConvPlugin_V34,
    },
    "codec1": {
        "suffix": "Codec1:",
        "class": ophyd.areadetector.plugins.CodecPlugin_V34,
    },
    "fft1": {
        "suffix": "FFT1:",
        "class": ophyd.areadetector.plugins.FFTPlugin_V34,
    },
    "gather1": {
        "suffix": "Gather1:",
        "class": ophyd.areadetector.plugins.GatherNPlugin_V31,
    },
    "overlay1": {
        "suffix": "Over1:",
        "class": ophyd.areadetector.plugins.OverlayPlugin_V34,
    },
    "process1": {
        "suffix": "Proc1:",
        "class": ophyd.areadetector.plugins.ProcessPlugin_V34,
    },
    "roi1": {
        "suffix": "ROI1:",
        "class": ophyd.areadetector.plugins.ROIPlugin_V34,
    },
    "roi2": {
        "suffix": "ROI2:",
        "class": ophyd.areadetector.plugins.ROIPlugin_V34,
    },
    "roi3": {
        "suffix": "ROI3:",
        "class": ophyd.areadetector.plugins.ROIPlugin_V34,
    },
    "roi4": {
        "suffix": "ROI4:",
        "class": ophyd.areadetector.plugins.ROIPlugin_V34,
    },
    "roistat1": {
        "suffix": "ROIStat1:",
        "class": ophyd.areadetector.plugins.ROIStatPlugin_V34,
    },
    "scatter1": {
        "suffix": "Scatter1:",
        "class": ophyd.areadetector.plugins.ScatterPlugin_V34,
    },
    "stats1": {
        "suffix": "Stats1:",
        "class": ophyd.areadetector.plugins.StatsPlugin_V34,
    },
    "stats2": {
        "suffix": "Stats2:",
        "class": ophyd.areadetector.plugins.StatsPlugin_V34,
    },
    "stats3": {
        "suffix": "Stats3:",
        "class": ophyd.areadetector.plugins.StatsPlugin_V34,
    },
    "stats4": {
        "suffix": "Stats4:",
        "class": ophyd.areadetector.plugins.StatsPlugin_V34,
    },
    "stats5": {
        "suffix": "Stats5:",
        "class": ophyd.areadetector.plugins.StatsPlugin_V34,
    },
    "transform1": {
        "suffix": "Trans1:",
        "class": ophyd.areadetector.plugins.TransformPlugin_V34,
    },
    # file writers
    "hdf1": {
        "class": HDF5FileWriterPlugin,
        "read_path_template": None,
        "suffix": "HDF1:",
        "write_path_template": None,
    },
    "jpeg1": {
        "class": AD_EpicsFileNameJPEGPlugin,
        "read_path_template": None,
        "suffix": "JPEG1:",
        "write_path_template": None,
    },
    "magick1": {
        "class": ophyd.areadetector.plugins.MagickPlugin_V34,
        "read_path_template": None,
        "suffix": "Magick1:",
        "write_path_template": None,
    },
    "netcdf1": {
        "class": ophyd.areadetector.plugins.NetCDFPlugin_V34,
        "read_path_template": None,
        "suffix": "netCDF1:",
        "write_path_template": None,
    },
    "tiff1": {
        "class": AD_EpicsFileNameTIFFPlugin,
        "read_path_template": None,
        "suffix": "TIFF1:",
        "write_path_template": None,
    },
}
"""Default plugin configuration dictionary."""


def ad_class_factory(name, bases=None, plugins=None, plugin_defaults=None):
    """
    Build an Area Detector class with specified plugins.

    PARAMETERS

    name
        *str* :
        Name of the class to be created.
    bases
        *object* or *tuple* :
        Parent(s) of the new class.
        (default: ``(SingleTrigger_V34, DetectorBase)``)
    plugins
        *list* :
        Description of the plugins used.
        (default: ``["cam"]`` -- Just the camera plugin.)
    plugin_defaults
        *object*:
        Plugin configuration dictionary.
        (default: ``None``, PLUGIN_DEFAULTS will be used.)
    """
    bases = bases or (
        SingleTrigger_V34,
        ophyd.areadetector.DetectorBase,
    )
    plugins = plugins or ["cam"]
    plugin_defaults = plugin_defaults or PLUGIN_DEFAULTS

    attributes = {}
    for spec in plugins:
        if isinstance(spec, dict):
            config = list(spec.values())[0]
            key = list(spec.keys())[0]
        elif isinstance(spec, str):
            key = spec
            config = {}
        else:
            raise ValueError(f"Unknown plugin configuration: {spec!r}")

        kwargs = plugin_defaults.get(key, {}).copy()  # default settings for this key
        kwargs.update(config)  # settings supplied by the caller
        if "class" not in kwargs:
            raise KeyError(f"Must define 'class': {kwargs=!r}")
        if "suffix" not in kwargs:
            raise KeyError(f"Must define 'suffix': {kwargs}")
        component_class = kwargs.pop("class")
        suffix = kwargs.pop("suffix")

        # if "write_path_template" in defaults
        attributes[key] = ADComponent(component_class, suffix, **kwargs)

    return type(name, bases, attributes)


def ad_creator(
    prefix: str,
    *,
    ad_setup: object = None,
    bases=None,
    class_name: str = None,
    name: str = None,
    plugin_defaults: dict = None,
    plugins=None,
    **kwargs,
):
    """
    Create an area detector object from a custom class.

    PARAMETERS

    prefix
        *str*:
        EPICS PV prefix.
    name
        *str*:
        Name of the ophyd object.
    class_name
        *str*:
        Name of the class to be created.
        (default: ``"ADclass_HEX7"`` where HEX is a random
        7-digit hexadecimal string)
    plugins
        *list*:
        Description of the plugins used.
    bases
        *object* or *tuple* :
        Parent(s) of the new class.
        (default: ``(SingleTrigger_V34, DetectorBase)``)
    ad_setup
        *object*:
        Optional setup function to be called.
        (default: ``None``)
    plugin_defaults
        *object*:
        Plugin configuration dictionary.
        (default: ``None``, PLUGIN_DEFAULTS will be used.)
    kwargs *dict*:
        Any additional keyword arguments for the new class definition.
        (default: ``{}``)
    """
    class_name = class_name or f"ADclass_{str(uuid.uuid4())[:7]}"
    ad_class = ad_class_factory(
        class_name,
        bases,
        plugins,
        plugin_defaults=plugin_defaults,
    )
    det = ad_class(prefix, name=name, **kwargs)
    det.validate_asyn_ports()
    if ad_setup is not None:
        # user-defined setup of the detector
        ad_setup(det)
    return det
