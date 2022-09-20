"""
EPICS PV Registry
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~findbyname
   ~findbypv
   ~PVRegistry
"""

import logging
import ophyd

from collections import defaultdict

from . import ipython_shell_namespace
from . import full_dotted_name


logger = logging.getLogger(__name__)


_findpv_registry = None


class PVRegistry:
    """
    Cross-reference EPICS PVs with ophyd EpicsSignalBase objects.
    """

    def __init__(self, ns=None):
        """
        Search ophyd objects for PV or ophyd names.

        The rebuild starts with the IPython console namespace
        (and defaults to the global namespace if the former
        cannot be obtained).

        PARAMETERS

        ns *dict* or `None`: namespace dictionary
        """
        self._pvdb = defaultdict(lambda: defaultdict(list))
        self._odb = {}
        self._device_name = None
        self._known_device_names = []
        g = ns or ipython_shell_namespace() or globals()

        # kickoff the registration process
        # fmt: off
        logger.debug(
            "Cross-referencing EPICS PVs with Python objects & ophyd symbols"
        )
        # fmt: on
        self._ophyd_epicsobject_walker(g)

    def _ophyd_epicsobject_walker(self, parent):
        """
        Walk through the parent object for ophyd Devices & EpicsSignals.

        This function is used to rebuild the ``self._pvdb`` object.
        """
        if isinstance(parent, dict):
            keys = parent.keys()
        else:
            keys = parent.component_names
            _nm_base = self._device_name
        for k in keys:
            if isinstance(parent, dict):
                _nm_base = []
                v = self._ref_dict(parent, k)
            else:
                v = self._ref_object_attribute(parent, k)
            if v is None:
                continue
            # print(k, type(v))
            if isinstance(v, ophyd.signal.EpicsSignalBase):
                try:
                    self._signal_processor(v)
                    self._odb[v.name] = ".".join(self._device_name + [k])
                except (KeyError, RuntimeError) as exc:
                    # fmt: off
                    logger.error(
                        "Exception while examining key '%s': (%s)", k, exc
                    )
                    # fmt: on
            elif isinstance(v, ophyd.Device):
                # print("Device", v.name)
                self._device_name = _nm_base + [k]
                if v.name not in self._known_device_names:
                    self._odb[v.name] = ".".join(self._device_name)
                    self._known_device_names.append(v.name)
                    self._ophyd_epicsobject_walker(v)

    def _ref_dict(self, parent, key):
        """Accessor used by ``_ophyd_epicsobject_walker()``"""
        return parent[key]

    def _ref_object_attribute(self, parent, key):
        """Accessor used by ``_ophyd_epicsobject_walker()``"""
        try:
            obj = getattr(parent, key, None)
            return obj
        except (KeyError, RuntimeError, TimeoutError) as exc:
            # fmt: off
            logger.error(
                "Exception while getting object '%s.%s': (%s)",
                ".".join(self._device_name), key, exc,
            )
            # fmt: on

    def _register_signal(self, signal, pv, mode):
        """Register a signal with the given mode."""
        fdn = full_dotted_name(signal)
        if fdn not in self._pvdb[pv][mode]:
            self._pvdb[pv][mode].append(fdn)

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
        return self._pvdb[pvname][mode]

    def search(self, pvname):
        """Search for PV in both read & write modes."""
        return dict(
            read=self.search_by_mode(pvname, "R"),
            write=self.search_by_mode(pvname, "W"),
        )

    def ophyd_search(self, oname):
        """Search for ophyd object by ophyd name."""
        return self._odb.get(oname)


def _get_pv_registry(force_rebuild, ns):
    """
    Check if need to build/rebuild the PV registry.

    PARAMETERS

    force_rebuild
        *bool* :
        If ``True``, rebuild the internal registry that maps
        EPICS PV names to ophyd objects.
    ns
        *dict* or `None` :
        Namespace dictionary of Python objects.

    """
    global _findpv_registry
    if _findpv_registry is None or force_rebuild:
        _findpv_registry = PVRegistry(ns=ns)
    return _findpv_registry


def findbyname(oname, force_rebuild=False, ns=None):
    """
    Find the ophyd (dotted name) object associated with the given ophyd name.

    PARAMETERS

    oname
        *str* :
        ophyd name to search
    force_rebuild
        *bool* :
        If ``True``, rebuild the internal registry that maps
        ophyd names to ophyd objects.
    ns
        *dict* or `None` :
        Namespace dictionary of Python objects.

    RETURNS

    str or ``None``:
        Name of the ophyd object.

    EXAMPLE::

        In [45]: findbyname("adsimdet_cam_acquire")
        Out[45]: 'adsimdet.cam.acquire'

    (new in apstools 1.5.0)
    """
    return _get_pv_registry(force_rebuild, ns).ophyd_search(oname)


def findbypv(pvname, force_rebuild=False, ns=None):
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
    ns
        *dict* or `None` :
        Namespace dictionary of Python objects.

    RETURNS

    dict or ``None``:
        Dictionary of matching ophyd objects, keyed by how the
        PV is used by the ophyd signal.  The keys are
        ``read`` and ``write``.

    EXAMPLE::

        In [45]: findbypv("ad:cam1:Acquire")
        Out[45]: {'read': [], 'write': ['adsimdet.cam.acquire']}

        In [46]: findbypv("ad:cam1:Acquire_RBV")
        Out[46]: {'read': ['adsimdet.cam.acquire'], 'write': []}

    """
    return _get_pv_registry(force_rebuild, ns).search(pvname)

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
