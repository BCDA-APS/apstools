
"""
send email

.. autosummary::
   
   ~EmailNotifications
"""

__all__ = ["EmailNotifications",]

import logging
logger = logging.getLogger(__name__)

from email.mime.text import MIMEText
import smtplib
from .decorators import run_in_thread


class EmailNotifications(object):
    """
    send email notifications when requested
    
    use default OS mail utility (so no credentials needed)
    """
    
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
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = ",".join(self.addresses)
        s = smtplib.SMTP(self.smtp_host)
        s.sendmail(self.sender, self.addresses, msg.as_string())
        s.quit()
