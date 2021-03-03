#!/usr/bin/env python

"""
Locate an ophyd object by the EPICS PV it uses.

.. autosummary::

   ~findpv

USAGE::

    In [51]: %run -im pv_finder

    In [52]: findpv("ad:cam1:Acquire_RBV")
    Out[52]: {'read': ['adsimdet.cam.acquire'], 'write': []}

    In [53]: findpv("ad:cam1:Acquire")
    Out[53]: {'read': [], 'write': ['adsimdet.cam.acquire']}
"""

__all__ = [
    "findpv",
]

from .utils import full_dotted_name
from .utils import ipython_shell_namespace
from collections import defaultdict
from ophyd import Device
from ophyd.signal import EpicsSignalBase


_registry = None


class PVRegistry:
    """
    Cross-reference EPICS PVs with ophyd EpicsSignalBase objects.
    """

    def __init__(self):
        """
        Search ophyd objects for PV names.

        The rebuild starts with the IPython console namespace
        (and defaults to the global namespace if the former
        cannot be obtained).
        """
        self._db = defaultdict(lambda: defaultdict(list))
        self._known_device_names = []
        if (g := ipython_shell_namespace()) == 0:
            # fallback
            g = globals()
        self._ophyd_epicsobject_walker(g)

    def _ophyd_epicsobject_walker(self, parent):
        """
        Walk through the parent object for ophyd Devices & EpicsSignals.

        This function is used to rebuild the ``self._db`` object.
        """
        if isinstance(parent, dict):
            keys = parent.keys()
            ref_func = self._ref_dict
        else:
            keys = parent.component_names
            ref_func = self._ref_object_attribute
        for k in keys:
            if (v := ref_func(parent, k)) is None:
                continue
            # print(k, type(v))
            if isinstance(v, EpicsSignalBase):
                self._signal_processor(v)
            elif isinstance(v, Device):
                # print("Device", v.name)
                if v.name not in self._known_device_names:
                    self._known_device_names.append(v.name)
                    self._ophyd_epicsobject_walker(v)

    def _ref_dict(self, parent, key):
        """Accessor used by ``_ophyd_epicsobject_walker()``"""
        return parent[key]

    def _ref_object_attribute(self, parent, key):
        """Accessor used by ``_ophyd_epicsobject_walker()``"""
        return getattr(parent, key)

    def _register_signal(self, signal, pv, mode):
        """Register a signal with the given mode."""
        if (fdn := full_dotted_name(signal)) not in self._db[pv][mode]:
            self._db[pv][mode].append(fdn)

    def _signal_processor(self, signal):
        """Register a signal's read & write PVs."""
        self._register_signal(signal, signal._read_pv.pvname, "R")
        if hasattr(signal, "_write_pv"):
            self._register_signal(signal, signal._write_pv.pvname, "W")

    def search_by_mode(self, pvname, mode="R"):
        """Search for PV in specified mode."""
        if mode not in ["R", "W"]:
            raise ValueError(
                f"Incorrect mode given ({mode}." "  Must be either `R` or `W`."
            )
        return self._db[pvname][mode]

    def search(self, pvname):
        """Search for PV in both read & write modes."""
        return dict(
            read=self.search_by_mode(pvname, "R"),
            write=self.search_by_mode(pvname, "W"),
        )


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
    global _registry
    if _registry is None or force_rebuild:
        _registry = PVRegistry()
    return _registry.search(pvname)
