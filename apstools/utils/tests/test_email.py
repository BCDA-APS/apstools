"""
Tests for EmailNotifications.

Verifies that the class initialises correctly, manages recipient addresses,
and constructs and sends email messages with the expected headers, without
requiring a real SMTP server.  See issue #1112.
"""

from contextlib import nullcontext as does_not_raise
from unittest import mock

import pytest

from ..email import EmailNotifications


@pytest.mark.parametrize(
    "sender, expected_sender, context",
    [
        pytest.param(
            None,
            "nobody@localhost",
            does_not_raise(),
            id="default sender when None",
        ),
        pytest.param(
            "user@example.com",
            "user@example.com",
            does_not_raise(),
            id="custom sender is stored as-is",
        ),
    ],
)
def test_email_notifications_init(sender, expected_sender, context):
    """EmailNotifications initialises with correct defaults."""
    with context:
        en = EmailNotifications(sender)
        assert en.sender == expected_sender
        assert en.addresses == []
        assert en.smtp_host == "localhost"
        assert en.notify_on_feedback is True


@pytest.mark.parametrize(
    "addresses, expected, context",
    [
        pytest.param(
            ["a@example.com"],
            ["a@example.com"],
            does_not_raise(),
            id="single address",
        ),
        pytest.param(
            ["a@example.com", "b@example.com"],
            ["a@example.com", "b@example.com"],
            does_not_raise(),
            id="multiple addresses added at once",
        ),
        pytest.param(
            [],
            [],
            does_not_raise(),
            id="no addresses added leaves list empty",
        ),
    ],
)
def test_add_addresses(addresses, expected, context):
    """add_addresses() appends all given addresses to the list."""
    with context:
        en = EmailNotifications()
        en.add_addresses(*addresses)
        assert en.addresses == expected


@pytest.mark.parametrize(
    "sender, addresses, subject, message, assertions, context",
    [
        pytest.param(
            "from@example.com",
            ["to@example.com"],
            "Test subject",
            "Test message body",
            {
                "from": "from@example.com",
                "to": "to@example.com",
                "subject": "Test subject",
                "body": "Test message body",
            },
            does_not_raise(),
            id="single recipient: headers and body are correct",
        ),
        pytest.param(
            "from@example.com",
            ["a@example.com", "b@example.com"],
            "Multi recipient",
            "Hello everyone",
            {
                "from": "from@example.com",
                "to": "a@example.com,b@example.com",
                "subject": "Multi recipient",
                "body": "Hello everyone",
            },
            does_not_raise(),
            id="multiple recipients: To header is comma-joined",
        ),
    ],
)
def test_send(sender, addresses, subject, message, assertions, context):
    """send() constructs the correct MIME message and calls SMTP sendmail."""
    en = EmailNotifications(sender)
    en.add_addresses(*addresses)

    captured = {}

    def fake_sendmail(from_addr, to_addrs, msg_string):
        import email as email_lib

        parsed = email_lib.message_from_string(msg_string)
        captured["from"] = parsed["From"]
        captured["to"] = parsed["To"]
        captured["subject"] = parsed["Subject"]
        captured["body"] = parsed.get_payload()

    mock_smtp_instance = mock.MagicMock()
    mock_smtp_instance.sendmail.side_effect = fake_sendmail

    with context:
        with mock.patch("apstools.utils.email.smtplib.SMTP", return_value=mock_smtp_instance):
            thread = en.send(subject, message)
            thread.join()  # wait for the background thread to complete

        for key, expected in assertions.items():
            assert captured[key] == expected

        mock_smtp_instance.quit.assert_called_once()
