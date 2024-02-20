"""
Scaler support
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~use_EPICS_scaler_channels
"""

import epics
from ophyd import EpicsScaler
from ophyd.scaler import ScalerCH

# for convenience
SCALER_AUTOCOUNT_MODE = 1  # TODO: contribute to ophyd?


def use_EPICS_scaler_channels(scaler):
    """
    configure scaler for only the channels with names assigned in EPICS

    Note: For `ScalerCH`, use `scaler.select_channels(None)` instead of this code.
    (Applies only to `ophyd.scaler.ScalerCH` in releases after 2019-02-27.)
    """
    if isinstance(scaler, EpicsScaler):
        read_attrs = []
        for ch in scaler.channels.component_names:
            _nam = epics.caget(f"{scaler.prefix}.NM{int(ch[4:])}")
            if len(_nam.strip()) > 0:
                read_attrs.append(ch)
        scaler.channels.read_attrs = read_attrs
    elif isinstance(scaler, ScalerCH):
        # superceded by: https://github.com/NSLS-II/ophyd/commit/543e7ef81f3cb760192a0de719e51f9359642ae8
        scaler.match_names()
        read_attrs = []
        configuration_attrs = []
        for ch in scaler.channels.component_names:
            nm_pv = scaler.channels.__getattribute__(ch)
            if nm_pv is not None and len(nm_pv.chname.get().strip()) > 0:
                read_attrs.append(ch)
                configuration_attrs.append(ch)
                configuration_attrs.append(ch + ".chname")
                configuration_attrs.append(ch + ".preset")
                configuration_attrs.append(ch + ".gate")
        scaler.channels.read_attrs = read_attrs
        scaler.channels.configuration_attrs = configuration_attrs


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2024, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
