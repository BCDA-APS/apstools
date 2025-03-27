"""
Scaler support
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~use_EPICS_scaler_channels
"""

from typing import Any, Dict, List, Optional, Union

import epics
from ophyd import EpicsScaler
from ophyd.scaler import ScalerCH

# for convenience
SCALER_AUTOCOUNT_MODE = 1  # TODO: contribute to ophyd?


def use_EPICS_scaler_channels(scaler: Union[EpicsScaler, ScalerCH]) -> None:
    """
    Configure scaler for only the channels with names assigned in EPICS.

    This function configures the read_attrs and configuration_attrs of a scaler
    based on the channel names assigned in EPICS. For ScalerCH devices, it uses
    the match_names() method and sets up both read and configuration attributes.
    For EpicsScaler devices, it checks each channel's name in EPICS and adds
    only those with non-empty names to read_attrs.

    Note: For `ScalerCH`, use `scaler.select_channels(None)` instead of this code.
    (Applies only to `ophyd.scaler.ScalerCH` in releases after 2019-02-27.)

    Args:
        scaler: An instance of either EpicsScaler or ScalerCH to configure

    Raises:
        ValueError: If the scaler is not an instance of EpicsScaler or ScalerCH
    """
    if isinstance(scaler, EpicsScaler):
        read_attrs: List[str] = []
        for ch in scaler.channels.component_names:
            _nam = epics.caget(f"{scaler.prefix}.NM{int(ch[4:])}")
            if len(_nam.strip()) > 0:
                read_attrs.append(ch)
        scaler.channels.read_attrs = read_attrs
    elif isinstance(scaler, ScalerCH):
        # superceded by: https://github.com/NSLS-II/ophyd/commit/543e7ef81f3cb760192a0de719e51f9359642ae8
        scaler.match_names()
        read_attrs: List[str] = []
        configuration_attrs: List[str] = []
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
    else:
        raise ValueError(f"Unsupported scaler type: {type(scaler)}")


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
