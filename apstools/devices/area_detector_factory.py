"""
Area Detector Factory
+++++++++++++++++++++

.. autosummary::

   ~ad_creator
   ~ad_class_factory
   ~REMOVE_DEFAULT_KEY

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

Remove a default key from a pre-configured plugin, this example removes the
``write_path_template`` key::

    from ophyd.areadetector import EigerDetectorCam
    from apstools.devices import ad_creator, REMOVE_DEFAULT_KEY

    det = ad_creator(
        "MyEiger", "ad:", "det",
        [
            {"cam": {"class": EigerDetectorCam}},
            "image",
            {"hdf1": {"write_path_template": REMOVE_DEFAULT_KEY}},
        ],
    )
"""

import logging

logger = logging.getLogger(__name__)

from ophyd import ADComponent
from ophyd.areadetector import CamBase
from ophyd.areadetector import DetectorBase
from ophyd.areadetector.plugins import CodecPlugin_V34
from ophyd.areadetector.plugins import ImagePlugin_V34
from ophyd.areadetector.plugins import OverlayPlugin_V34
from ophyd.areadetector.plugins import ProcessPlugin_V34
from ophyd.areadetector.plugins import PvaPlugin_V34
from ophyd.areadetector.plugins import ROIPlugin_V34
from ophyd.areadetector.plugins import StatsPlugin_V34
from ophyd.areadetector.plugins import TransformPlugin_V34

from .area_detector_support import HDF5FileWriterPlugin
from .area_detector_support import SingleTrigger_V34

PLUGIN_DEFAULTS = {  # some of the common plugins
    # gets image from the detector
    "cam": {"suffix": "cam1:", "class": CamBase},

    # for imaging
    "image": {"suffix": "image1:", "class": ImagePlugin_V34},
    "pva": {"suffix": "Pva1:", "class": PvaPlugin_V34},

    # signal handling
    # TODO: "attr1": {"suffix": "Attr1:", "class": AttributePlugin_V34},
    # TODO: "badpix1": {"suffix": "BadPix1:", "class": BadPixelPlugin_V34},
    # TODO: "cb1": {"suffix": "CB1:", "class": CircularBufferPlugin_V34},
    # TODO: "cc1": {"suffix": "CC1:", "class": ColorConverterPlugin_V34},
    # TODO: "cc2": {"suffix": "CC2:", "class": ColorConverterPlugin_V34},
    # TODO: "fft1": {"suffix": "FFT1:", "class": FFTPlugin_V34},
    # TODO: "roistat1": {"suffix": "ROIStat1:", "class": ROIStatPlugin_V34},
    # TODO: "scatter1": {"suffix": "Scatter1:", "class": ScatterPlugin_V34},
    # TODO: "gather1": {"suffix": "Gather1:", "class": GatherPlugin_V34},
    "codec1": {"suffix": "Codec1:", "class": CodecPlugin_V34},
    "overlay1": {"suffix": "Over1:", "class": OverlayPlugin_V34},
    "process1": {"suffix": "Proc1:", "class": ProcessPlugin_V34},
    "roi1": {"suffix": "ROI1:", "class": ROIPlugin_V34},
    "roi2": {"suffix": "ROI2:", "class": ROIPlugin_V34},
    "roi3": {"suffix": "ROI3:", "class": ROIPlugin_V34},
    "roi4": {"suffix": "ROI4:", "class": ROIPlugin_V34},
    "stats1": {"suffix": "Stats1:", "class": StatsPlugin_V34},
    "stats2": {"suffix": "Stats2:", "class": StatsPlugin_V34},
    "stats3": {"suffix": "Stats3:", "class": StatsPlugin_V34},
    "stats4": {"suffix": "Stats4:", "class": StatsPlugin_V34},
    "stats5": {"suffix": "Stats5:", "class": StatsPlugin_V34},
    "transform1": {"suffix": "Trans1:", "class": TransformPlugin_V34},

    # file writers
    "hdf1": {
        "suffix": "HDF1:",
        "class": HDF5FileWriterPlugin,
        "write_path_template": None,
        "read_path_template": None,
    },
    # TODO: "jpeg1": {
    #     "suffix": "JPEG1:",
    #     "class": JPEGPlugin_V34,  # TODO: JPEGFileWriterPlugin
    #     "write_path_template": None,
    #     "read_path_template": None,
    # },
    # # TODO: "magick1": {
    # #     "suffix": "Magick1:",
    # #     "class": MagickPlugin_V34,
    # #     "write_path_template": None,
    # #     "read_path_template": None,
    # # },
    # # TODO: "netcdf1": {
    # #     "suffix": "netCDF1:",
    # #     "class": NetCDFPlugin_V34,
    # #     "write_path_template": None,
    # #     "read_path_template": None,
    # # },
    # TODO: "tiff1": {
    #     "suffix": "TIFF1:",
    #     "class": TIFFPlugin_V34,  # TODO: TIFFFileWriterPlugin
    #     "write_path_template": None,
    #     "read_path_template": None,
    # },
}

REMOVE_DEFAULT_KEY = object()
"""Flag to remove a plugin configuration key."""


def ad_class_factory(name, bases, plugins):
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
    """
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

        kwargs = PLUGIN_DEFAULTS.get(key, {}).copy()  # default settings for this key
        kwargs.update(config)  # settings supplied by the caller
        if "class" not in kwargs:
            raise KeyError(f"'class' cannot be 'None': {kwargs=!r}")
        if "suffix" not in kwargs:
            raise KeyError(f"'suffix' cannot be 'None': {kwargs}")
        component_class = kwargs.pop("class")
        suffix = kwargs.pop("suffix")

        for k in list(kwargs):
            if kwargs[k] == REMOVE_DEFAULT_KEY:
                kwargs.pop(k)

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
    kwargs *dict*:
        Any additional keyword arguments for the new class definition.
        (default: ``{}``)
    """
    bases = bases or (SingleTrigger_V34, DetectorBase)

    ad_class = ad_class_factory(class_name, bases, plugins)
    det = ad_class(prefix, name=name, **kwargs)
    det.validate_asyn_ports()
    if ad_setup is not None:
        # user-defined setup of the detector
        ad_setup(det)
    return det
