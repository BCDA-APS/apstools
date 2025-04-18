"""
email Support
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~EmailNotifications
"""

import smtplib
from email.mime.text import MIMEText
from typing import List, Optional

from .misc import run_in_thread


class EmailNotifications:
    """
    send email notifications when requested

    .. index:: apstools Utility; EmailNotifications

    use default OS mail utility (so no credentials needed)

    EXAMPLE

    Send email(s) when `feedback_limits_approached`
    (a hypothetical boolean) is `True`::

        # setup
        from apstools.utils import EmailNotifications

        SENDER_EMAIL = "instrument_user@email.host.tld"

        email_notices = EmailNotifications(SENDER_EMAIL)
        email_notices.add_addresses(
            # This list receives email when send() is called.
            "joe.user@goodmail.com",
            "instrument_team@email.host.tld",
            # others?
        )

        # ... later

        if feedback_limits_approached:
            # send emails to list
            subject = "Feedback problem"
            message = "Feedback is very close to its limits."
            email_notices.send(subject, message)
    """

    def __init__(self, sender: Optional[str] = None) -> None:
        """
        Initialize the email notifications system.

        Parameters
        ----------
        sender : Optional[str]
            The email address to send from. If None, defaults to "nobody@localhost".
        """
        self.addresses: List[str] = []
        self.notify_on_feedback: bool = True
        self.sender: str = sender or "nobody@localhost"
        self.smtp_host: str = "localhost"

    def add_addresses(self, *args: str) -> None:
        """
        Add email addresses to the notification list.

        Parameters
        ----------
        *args : str
            One or more email addresses to add to the notification list.
        """
        for address in args:
            self.addresses.append(address)

    @run_in_thread
    def send(self, subject: str, message: str) -> None:
        """
        Send an email message to all registered addresses.

        Parameters
        ----------
        subject : str
            The email subject line.
        message : str
            The email message body.
        """
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = ",".join(self.addresses)
        s = smtplib.SMTP(self.smtp_host)
        s.sendmail(self.sender, self.addresses, msg.as_string())
        s.quit()


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2017-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
