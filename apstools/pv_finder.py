#!/usr/bin/env python

"""
Locate an ophyd object by the EPICS PV it uses.

.. autosummary::

   ~findpv
"""

__all__ = [
    "findpv",
]

from .utils import full_dotted_name
from .utils import ipython_shell_namespace
from collections import defaultdict
from collections import namedtuple
from ophyd import Device
from ophyd.signal import EpicsSignalBase


_known_device_names = []
_registry = None


def _build_registry(force_rebuild=False):
    """Check the ``_registry`` object and rebuild it if needed."""
    global _registry
    if _registry is None or force_rebuild:
        _registry = defaultdict(list)
        g = ipython_shell_namespace()
        if len(g) == 0:
            # fallback
            g = globals()
        _ophyd_epicsobject_walker(g)


def _ref_dict(parent, key):
    """Accessor used by ``_ophyd_epicsobject_walker()``"""
    return parent[key]


def _ref_object_attribute(parent, key):
    """Accessor used by ``_ophyd_epicsobject_walker()``"""
    return getattr(parent, key)


def _register_signal(signal, pv, mode):
    """Register a signal with the given mode."""
    key = f"{mode}: {pv}"
    if (fdn := full_dotted_name(signal)) not in _registry[key]:
        _registry[key].append(fdn)


def _signal_processor(signal):
    """Register a signal's read & write PVs."""
    _register_signal(signal, signal._read_pv.pvname, "R")
    if hasattr(signal, "_write_pv"):
        _register_signal(signal, signal._write_pv.pvname, "W")


def _ophyd_epicsobject_walker(parent):
    """
    Walk through the parent object for ophyd Devices & EpicsSignals.

    This function is used to rebuild the ``_registry`` object.
    """
    if isinstance(parent, dict):
        keys = parent.keys()
        ref_func = _ref_dict
    else:
        keys = parent.component_names
        ref_func = _ref_object_attribute
    for k in keys:
        if (v := ref_func(parent, k)) is None:
            continue
        # print(k, type(v))
        if isinstance(v, EpicsSignalBase):
            _signal_processor(v)
        elif isinstance(v, Device):
            # print("Device", v.name)
            if v.name not in _known_device_names:
                _known_device_names.append(v.name)
                _ophyd_epicsobject_walker(v)


def findpv(pvname, force_rebuild=False):
    """
    Find all ophyd objects associated with the given EPICS PV.

    PARAMETERS

    pvname
        *str* :
        EPICS PV name to search
    force_rebuild
        *bool* :
        If ``True``, rebuild the internal registry that maps
        EPICS PV names to ophyd objects.

    RETURNS

    dict or ``None``:
        Dictionary of matching ophyd objects, keyed by how the
        PV is used by the ophyd signal.  The keys are
        ``read`` and ``write``.

    EXAMPLE::

        In [45]: findpv("ad:cam1:Acquire")
        Out[45]: {'read': [], 'write': ['adsimdet.cam.acquire']}

        In [46]: findpv("ad:cam1:Acquire_RBV")
        Out[46]: {'read': ['adsimdet.cam.acquire'], 'write': []}

    """
    _build_registry(force_rebuild=force_rebuild)
    return dict(read=_registry[f"R: {pvname}"], write=_registry[f"W: {pvname}"])
