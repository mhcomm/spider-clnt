#!/usr/bin/env python

# #############################################################################
# Copyright : (C) 2024 by MHComm. All rights reserved
#
# Name       :  spider_clt.mta
"""
  Summary : send mail via spider api

__author__ = "Klaus Foerster"
__email__ = "info@mhcomm.fr"

Simple MTA that sends mails via spider API
"""
# #############################################################################
import email
import logging

import requests

from spider_clnt.common import vprint


logger = logging.getLogger(__name__)


def fmt_recipients(recipients):
    """
    helper to format mail recipients
    """
    return [
        addr.strip()
        for addr in recipients
    ]


def parse_email_message(raw_data):
    """
    extract headers, body, attachments from raw email text
    """
    msg = email.message_from_string(raw_data)

    to_addrs = msg.get_all("To", [])
    cc_addrs = msg.get_all("Cc", [])
    bcc_addrs = msg.get_all("Bcc", [])
    assert not bcc_addrs, "must implement bcc handling"

    # Microsoft Graph does not support BCC directly
    # — skip it or handle differently

    recipients = fmt_recipients(to_addrs + cc_addrs)

    subject = msg.get("Subject", "")
    content_type = "text/plain"
    content = ""

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                content = (
                    part.get_payload(decode=True)
                    .decode(part.get_content_charset("utf-8"))
                )
                break
    else:
        content = (
            msg.get_payload(decode=True)
            .decode(msg.get_content_charset("utf-8"))
        )

    return subject, recipients, content_type, content


def get_html_from_text(text):
    """
    converts text mail into an html mail
    """
    # TODO: This must be improved. There is no escaping at all
    return f"<!DOCTYPE html><html><body><p>{text}</p></body></html> "


class SpiderClient:
    def __init__(self, url, username, password, sender=None):
        self.url = url
        self.username = username
        self.password = password
        self.sender = sender
        self.ses = requests.Session()
        self.token = None
        self.headers = None

    def login(self):
        """
        Authenticate
        """
        credentials = {"username": self.username, "password": self.password}
        resp = self.ses.post(f"{self.url}/api/v1/login", json=credentials)
        json_resp = resp.json()
        self.token = json_resp["accessToken"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def send_mail(
        self,
        recipients,
        subject,
        content_type,
        content,
        sender,
        html=None,
    ):
        """
        sends an email
        """
        # TODO: check for CC, BCC and attachment handling
        results = []
        for recipient in recipients:
            if not html:
                html = get_html_from_text(content)
            data = {
                "from": self.sender,
                "fromName": "From Name",
                "to": recipient,
                "subject": subject,
                "text": content,
                "html": html,
                "files": [],
            }
            vprint(f"{data=}")
            rslt = self.ses.post(
                f"{self.url}/api/v1/sendmail",
                json=data, headers=self.headers)
            results.append(rslt)
        return results

    def send_sms(
        self,
        recipient,
        content,
        sender,
    ):
        """
        send SMS to one recipient
        """
        data = {
            "sender": self.sender,
            "recipient": recipient,
            "text": content,
        }
        rslt = self.ses.post(
            f"{self.url}/api/v1/sendsms",
            json=data, headers=self.headers)
        return rslt
