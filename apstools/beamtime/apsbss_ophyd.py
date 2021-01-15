#!/usr/bin/env python

"""
ophyd support for apsbss

EXAMPLE::

    apsbss = EpicsBssDevice("ioc:bss:", name="apsbss")

.. autosummary::

    ~EpicsBssDevice
    ~EpicsEsafDevice
    ~EpicsEsafExperimenterDevice
    ~EpicsProposalDevice
    ~EpicsProposalExperimenterDevice

"""

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2021, UChicago Argonne, LLC
#
# Distributed under the terms of the Creative Commons Attribution 4.0 International Public License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------

__all__ = [
    "EpicsBssDevice",
]

from ..plans import addDeviceDataAsStream
from ophyd import Component, Device, EpicsSignal


class EpicsEsafExperimenterDevice(Device):
    """
    Ophyd device for experimenter info from APS ESAF.

    .. autosummary::

        ~clear
    """

    badge_number = Component(EpicsSignal, "badgeNumber", string=True)
    email = Component(EpicsSignal, "email", string=True)
    first_name = Component(EpicsSignal, "firstName", string=True)
    last_name = Component(EpicsSignal, "lastName", string=True)

    def clear(self):
        """Clear the fields for this user."""
        self.badge_number.put("")
        self.email.put("")
        self.first_name.put("")
        self.last_name.put("")


class EpicsEsafDevice(Device):
    """
    Ophyd device for info from APS ESAF.

    .. autosummary::

        ~clear
        ~clear_users
    """

    aps_cycle = Component(EpicsSignal, "cycle", string=True)
    description = Component(EpicsSignal, "description", string=True)
    end_date = Component(EpicsSignal, "endDate", string=True)
    esaf_id = Component(EpicsSignal, "id", string=True)
    esaf_status = Component(EpicsSignal, "status", string=True)
    number_users_in_pvs = Component(EpicsSignal, "users_in_pvs")
    number_users_total = Component(EpicsSignal, "users_total")
    raw = Component(EpicsSignal, "raw", string=True, kind="omitted")
    sector = Component(EpicsSignal, "sector", string=True)
    start_date = Component(EpicsSignal, "startDate", string=True)
    title = Component(EpicsSignal, "title", string=True)
    user_last_names = Component(EpicsSignal, "users", string=True)
    user_badges = Component(EpicsSignal, "userBadges", string=True)

    _max_users = 9  # 9 users at most?
    user1 = Component(EpicsEsafExperimenterDevice, "user1:")
    user2 = Component(EpicsEsafExperimenterDevice, "user2:")
    user3 = Component(EpicsEsafExperimenterDevice, "user3:")
    user4 = Component(EpicsEsafExperimenterDevice, "user4:")
    user5 = Component(EpicsEsafExperimenterDevice, "user5:")
    user6 = Component(EpicsEsafExperimenterDevice, "user6:")
    user7 = Component(EpicsEsafExperimenterDevice, "user7:")
    user8 = Component(EpicsEsafExperimenterDevice, "user8:")
    user9 = Component(EpicsEsafExperimenterDevice, "user9:")

    def clear(self):
        """
        Clear the most of the ESAF info.

        Do not clear these items:

        * ``aps_cycle``
        * ``esaf_id``
        * ``sector``
        """
        # self.aps_cycle.put("")    # user controls this
        self.description.put("")
        self.end_date.put("")
        # self.esaf_id.put("")      # user controls this
        self.esaf_status.put("")
        # self.sector.put("")
        self.start_date.put("")
        self.title.put("")
        self.user_last_names.put("")
        self.user_badges.put("")

        self.clear_users()

    def clear_users(self):
        """Clear the info for all users."""
        self.user1.clear()
        self.user2.clear()
        self.user3.clear()
        self.user4.clear()
        self.user5.clear()
        self.user6.clear()
        self.user7.clear()
        self.user8.clear()
        self.user9.clear()


class EpicsProposalExperimenterDevice(Device):
    """
    Ophyd device for experimenter info from APS Proposal.

    .. autosummary::

        ~clear
    """

    badge_number = Component(EpicsSignal, "badgeNumber", string=True)
    email = Component(EpicsSignal, "email", string=True)
    first_name = Component(EpicsSignal, "firstName", string=True)
    institution = Component(EpicsSignal, "institution", string=True)
    institution_id = Component(EpicsSignal, "instId", string=True)
    last_name = Component(EpicsSignal, "lastName", string=True)
    pi_flag = Component(EpicsSignal, "piFlag", string=True)
    user_id = Component(EpicsSignal, "userId", string=True)

    def clear(self):
        """Clear the info for this user."""
        self.badge_number.put("")
        self.email.put("")
        self.first_name.put("")
        self.last_name.put("")
        self.user_id.put("")
        self.institution_id.put("")
        self.institution.put("")
        self.pi_flag.put(0)


class EpicsProposalDevice(Device):
    """
    Ophyd device for info from APS Proposal.

    .. autosummary::

        ~clear
        ~clear_users
    """

    beamline_name = Component(EpicsSignal, "beamline", string=True)

    end_date = Component(EpicsSignal, "endDate", string=True)
    mail_in_flag = Component(EpicsSignal, "mailInFlag", string=True)
    number_users_in_pvs = Component(EpicsSignal, "users_in_pvs")
    number_users_total = Component(EpicsSignal, "users_total")
    proposal_id = Component(EpicsSignal, "id", string=True)
    proprietary_flag = Component(
        EpicsSignal, "proprietaryFlag", string=True
    )
    raw = Component(EpicsSignal, "raw", string=True, kind="omitted")
    start_date = Component(EpicsSignal, "startDate", string=True)
    submitted_date = Component(EpicsSignal, "submittedDate", string=True)
    title = Component(EpicsSignal, "title", string=True)
    user_badges = Component(EpicsSignal, "userBadges", string=True)
    user_last_names = Component(EpicsSignal, "users", string=True)

    _max_users = 9  # 9 users at most?
    user1 = Component(EpicsProposalExperimenterDevice, "user1:")
    user2 = Component(EpicsProposalExperimenterDevice, "user2:")
    user3 = Component(EpicsProposalExperimenterDevice, "user3:")
    user4 = Component(EpicsProposalExperimenterDevice, "user4:")
    user5 = Component(EpicsProposalExperimenterDevice, "user5:")
    user6 = Component(EpicsProposalExperimenterDevice, "user6:")
    user7 = Component(EpicsProposalExperimenterDevice, "user7:")
    user8 = Component(EpicsProposalExperimenterDevice, "user8:")
    user9 = Component(EpicsProposalExperimenterDevice, "user9:")

    def clear(self):
        """
        Clear the most of the proposal info.

        Do not clear these items:

        * ``beamline_name``
        * ``proposal_id``
        """
        # self.beamline_name.put("")    # user controls this
        self.end_date.put("")
        self.mail_in_flag.put(0)
        # self.proposal_id.put(-1)      # user controls this
        self.proprietary_flag.put(0)
        self.start_date.put("")
        self.submitted_date.put("")
        self.title.put("")
        self.user_last_names.put("")
        self.user_badges.put("")

        self.clear_users()

    def clear_users(self):
        """Clear the info for all users."""
        self.user1.clear()
        self.user2.clear()
        self.user3.clear()
        self.user4.clear()
        self.user5.clear()
        self.user6.clear()
        self.user7.clear()
        self.user8.clear()
        self.user9.clear()


class EpicsBssDevice(Device):
    """
    Ophyd device for info from APS Proposal and ESAF databases.

    .. autosummary::

        ~clear
    """

    esaf = Component(EpicsEsafDevice, "esaf:")
    proposal = Component(EpicsProposalDevice, "proposal:")

    ioc_host = Component(
        EpicsSignal, "ioc_host", string=True, kind="omitted"
    )
    ioc_user = Component(
        EpicsSignal, "ioc_user", string=True, kind="omitted"
    )
    status_msg = Component(
        EpicsSignal, "status", string=True, kind="omitted"
    )

    def clear(self):
        """Clear the proposal and ESAF info."""
        self.esaf.clear()
        self.proposal.clear()
        self.status_msg.put("Cleared")

    def addDeviceDataAsStream(self, stream_name=None):
        """write the data as streams"""
        stream_name = stream_name or "apsbss"
        yield from addDeviceDataAsStream(self, stream_name)
