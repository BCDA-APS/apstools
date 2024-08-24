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
    det = ad_creator("MySimpleAD", "ad:", "det", ["cam",])

View ADSimDetector image with CA and PVA::

    from ophyd.areadetector import SimDetectorCam
    from apstools.devices import ad_creator

    det = ad_creator(
        "MySimDetector", "ad:", "det",
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
        "MyEiger", "ad:", "det",
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
        "MyEiger", "ad:", "det",
        [
            {"cam": {"class": EigerDetectorCam}},
            "image",
            "hdf1",
        ],
        plugin_defaults=plugin_defaults,
    )
"""

import logging

logger = logging.getLogger(__name__)

from ophyd import ADComponent
from ophyd.areadetector import CamBase
from ophyd.areadetector import DetectorBase
from ophyd.areadetector.plugins import AttrPlotPlugin_V34
from ophyd.areadetector.plugins import CircularBuffPlugin_V34
from ophyd.areadetector.plugins import CodecPlugin_V34
from ophyd.areadetector.plugins import ColorConvPlugin_V34
from ophyd.areadetector.plugins import FFTPlugin_V34
from ophyd.areadetector.plugins import GatherNPlugin_V31
from ophyd.areadetector.plugins import ImagePlugin_V34
from ophyd.areadetector.plugins import MagickPlugin_V34
from ophyd.areadetector.plugins import NetCDFPlugin_V34
from ophyd.areadetector.plugins import OverlayPlugin_V34
from ophyd.areadetector.plugins import ProcessPlugin_V34
from ophyd.areadetector.plugins import PvaPlugin_V34
from ophyd.areadetector.plugins import ROIPlugin_V34
from ophyd.areadetector.plugins import ROIStatPlugin_V34
from ophyd.areadetector.plugins import ScatterPlugin_V34
from ophyd.areadetector.plugins import StatsPlugin_V34
from ophyd.areadetector.plugins import TransformPlugin_V34

from .area_detector_support import AD_EpicsFileNameJPEGPlugin
from .area_detector_support import AD_EpicsFileNameTIFFPlugin
from .area_detector_support import HDF5FileWriterPlugin
from .area_detector_support import SingleTrigger_V34

PLUGIN_DEFAULTS = {  # some of the common plugins
    # gets image from the detector
    "cam": {"suffix": "cam1:", "class": CamBase},
    # for imaging
    "image": {"suffix": "image1:", "class": ImagePlugin_V34},
    "pva": {"suffix": "Pva1:", "class": PvaPlugin_V34},
    # signal handling
    "attr1": {"suffix": "Attr1:", "class": AttrPlotPlugin_V34},
    "cb1": {"suffix": "CB1:", "class": CircularBuffPlugin_V34},
    "cc1": {"suffix": "CC1:", "class": ColorConvPlugin_V34},
    "cc2": {"suffix": "CC2:", "class": ColorConvPlugin_V34},
    "codec1": {"suffix": "Codec1:", "class": CodecPlugin_V34},
    "fft1": {"suffix": "FFT1:", "class": FFTPlugin_V34},
    "gather1": {"suffix": "Gather1:", "class": GatherNPlugin_V31},
    "overlay1": {"suffix": "Over1:", "class": OverlayPlugin_V34},
    "process1": {"suffix": "Proc1:", "class": ProcessPlugin_V34},
    "roi1": {"suffix": "ROI1:", "class": ROIPlugin_V34},
    "roi2": {"suffix": "ROI2:", "class": ROIPlugin_V34},
    "roi3": {"suffix": "ROI3:", "class": ROIPlugin_V34},
    "roi4": {"suffix": "ROI4:", "class": ROIPlugin_V34},
    "roistat1": {"suffix": "ROIStat1:", "class": ROIStatPlugin_V34},
    "scatter1": {"suffix": "Scatter1:", "class": ScatterPlugin_V34},
    "stats1": {"suffix": "Stats1:", "class": StatsPlugin_V34},
    "stats2": {"suffix": "Stats2:", "class": StatsPlugin_V34},
    "stats3": {"suffix": "Stats3:", "class": StatsPlugin_V34},
    "stats4": {"suffix": "Stats4:", "class": StatsPlugin_V34},
    "stats5": {"suffix": "Stats5:", "class": StatsPlugin_V34},
    "transform1": {"suffix": "Trans1:", "class": TransformPlugin_V34},
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
        "class": MagickPlugin_V34,
        "read_path_template": None,
        "suffix": "Magick1:",
        "write_path_template": None,
    },
    "netcdf1": {
        "class": NetCDFPlugin_V34,
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


def ad_class_factory(name, bases, plugins, plugin_defaults=None):
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
    plugin_defaults
        *object*:
        Plugin configuration dictionary.
        (default: ``None``, PLUGIN_DEFAULTS will be used.)
    """
    bases = bases or (SingleTrigger_V34, DetectorBase)
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
    class_name: str,
    prefix: str,
    name: str,
    plugins,
    bases=None,
    ad_setup: object = None,
    plugin_defaults: dict = None,
    **kwargs,
):
    """
    Create an area detector object from a custom class.

    PARAMETERS

    class_name
        *str*:
        Name of the class to be created.
    prefix
        *str*:
        EPICS PV prefix.
    name
        *str*:
        Name of the ophyd object.
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
