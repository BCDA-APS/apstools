"""
APS User Proposal and ESAF Information
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~ApsBssUserInfoDevice
"""

from ophyd import Component
from ophyd import Device
from ophyd import EpicsSignal


class ApsBssUserInfoDevice(Device):
    """
    Provide current experiment info from the APS BSS.

    .. index:: Ophyd Device; ApsBssUserInfoDevice

    BSS: Beamtime Scheduling System

    EXAMPLE::

        bss_user_info = ApsBssUserInfoDevice(
                            "9id_bss:",
                            name="bss_user_info")
        sd.baseline.append(bss_user_info)

    NOTE: There is info provided by the APS proposal & ESAF systems.
    """

    proposal_number = Component(EpicsSignal, "proposal_number")
    activity = Component(EpicsSignal, "activity", string=True)
    badge = Component(EpicsSignal, "badge", string=True)
    bss_name = Component(EpicsSignal, "bss_name", string=True)
    contact = Component(EpicsSignal, "contact", string=True)
    email = Component(EpicsSignal, "email", string=True)
    institution = Component(EpicsSignal, "institution", string=True)
    station = Component(EpicsSignal, "station", string=True)
    team_others = Component(EpicsSignal, "team_others", string=True)
    time_begin = Component(EpicsSignal, "time_begin", string=True)
    time_end = Component(EpicsSignal, "time_end", string=True)
    timestamp = Component(EpicsSignal, "timestamp", string=True)
    title = Component(EpicsSignal, "title", string=True)
    # not yet updated, see: https://git.aps.anl.gov/jemian/aps_bss_user_info/issues/10
    esaf = Component(EpicsSignal, "esaf", string=True)
    esaf_contact = Component(EpicsSignal, "esaf_contact", string=True)
    esaf_team = Component(EpicsSignal, "esaf_team", string=True)


# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
