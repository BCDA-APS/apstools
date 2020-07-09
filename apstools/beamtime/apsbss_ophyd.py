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

__all__ = ["EpicsBssDevice",]

from ophyd import Component, Device, EpicsSignal


class EpicsEsafExperimenterDevice(Device):
    """
    Ophyd device for experimenter info from APS ESAF.
    """
    badge_number = Component(EpicsSignal, "badgeNumber", string=True)
    email = Component(EpicsSignal, "email", string=True)
    first_name = Component(EpicsSignal, "firstName", string=True)
    last_name = Component(EpicsSignal, "lastName", string=True)

    def clear(self):
        self.badge_number.put("")
        self.email.put("")
        self.first_name.put("")
        self.last_name.put("")


class EpicsEsafDevice(Device):
    """
    Ophyd device for info from APS ESAF.
    """

    aps_cycle = Component(EpicsSignal, "cycle", string=True)
    description = Component(EpicsSignal, "description", string=True)
    end_date = Component(EpicsSignal, "endDate", string=True)
    esaf_id = Component(EpicsSignal, "id", string=True)
    esaf_status = Component(EpicsSignal, "status", string=True)
    sector = Component(EpicsSignal, "sector", string=True)
    start_date = Component(EpicsSignal, "startDate", string=True)
    title = Component(EpicsSignal, "title", string=True)
    user_last_names = Component(EpicsSignal, "users", string=True)
    user_badges = Component(EpicsSignal, "userBadges", string=True)

    _max_users = 9    # 9 users at most?
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
    """

    beamline_name = Component(EpicsSignal, "beamline", string=True)

    mail_in_flag = Component(EpicsSignal, "mailInFlag", string=True)
    proposal_id = Component(EpicsSignal, "id", string=True)
    proprietary_flag = Component(EpicsSignal, "proprietaryFlag", string=True)
    submitted_date = Component(EpicsSignal, "submittedDate", string=True)
    title = Component(EpicsSignal, "title", string=True)
    user_last_names = Component(EpicsSignal, "users", string=True)
    user_badges = Component(EpicsSignal, "userBadges", string=True)

    _max_users = 9    # 9 users at most?
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
        # self.beamline_name.put("")    # user controls this
        self.mail_in_flag.put(0)
        # self.proposal_id.put(-1)      # user controls this
        self.proprietary_flag.put(0)
        self.submitted_date.put("")
        self.title.put("")
        self.user_last_names.put("")
        self.user_badges.put("")

        self.clear_users()

    def clear_users(self):
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
    """

    esaf = Component(EpicsEsafDevice, "esaf:")
    proposal = Component(EpicsProposalDevice, "proposal:")

    def clear(self):
        self.esaf.clear()
        self.proposal.clear()
