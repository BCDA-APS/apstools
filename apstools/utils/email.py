"""
email Support
+++++++++++++++++++++++++++++++++++++++

.. autosummary::

   ~EmailNotifications
"""

import smtplib
from email.mime.text import MIMEText


class EmailNotifications(object):
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
    from .misc import run_in_thread

    def __init__(self, sender=None):
        self.addresses = []
        self.notify_on_feedback = True
        self.sender = sender or "nobody@localhost"
        self.smtp_host = "localhost"

    def add_addresses(self, *args):
        for address in args:
            self.addresses.append(address)

    @run_in_thread
    def send(self, subject, message):
        """send ``message`` to all addresses"""
        msg = MIMEText(message)
        msg["Subject"] = subject
        msg["From"] = self.sender
        msg["To"] = ",".join(self.addresses)
        s = smtplib.SMTP(self.smtp_host)
        s.sendmail(self.sender, self.addresses, msg.as_string())
        s.quit()

# -----------------------------------------------------------------------------
# :author:    Pete R. Jemian
# :email:     jemian@anl.gov
# :copyright: (c) 2017-2022, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
