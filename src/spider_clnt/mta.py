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
import argparse
import email
import json
import logging
import os
import sys

from pathlib import Path

import requests


logger = logging.getLogger(__name__)
CONFIG_FILE = Path.home() / ".config" / "spider_clnt.json"
VERBOSE = False


def vprint(*args, **kwargs):
    """
    print if verbose
    """
    if not VERBOSE:
        return
    print(*args, **kwargs)


def load_config(configfile):
    cfg_path = Path(configfile)
    with cfg_path.open() as fin:
        data = json.load(fin)
        entry = data["default"]
        return {
            # "tenant_id": entry["tenant_id"],
            # "client_id": entry["application_id"],
            # "client_secret": entry["secret_value"],
            # "from_address": entry["sender"],
        }




def fmt_recipients(recipients):
    return [
        {"emailAddress": {"address": addr.strip()}}
        for addr in recipients
    ]


def parse_email_message(raw_data):
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


def send_mail(token, sender, subject, recipients, content_type, content):
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    data = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": content
            },
            "toRecipients": recipients,
            "from": {
                "emailAddress": {"address": sender}
            }
        },
        "saveToSentItems": "true"
    }

    response = requests.post(
        f"{GRAPH_ENDPOINT}/users/{sender}/sendMail",
        headers=headers,
        json=data
    )

    if not response.ok:
        raise Exception(
            f"Graph sendMail failed: {response.status_code} {response.text}")

    logger.info("Message sent successfully")


def mk_parser():
    """ commandline parser """
    description = "no description given"
    default_cfg = str(CONFIG_FILE)
    default_cfg = os.environ.get("SPIDER_CLNT_CONFIG", default_cfg)

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        '--config',
        '-c',
        default=default_cfg,
        help="config file to read from: default=%(default)s",
    )
    parser.add_argument(
        '--verbose',
        '-v',
        action="store_true",
        help="be a little more verbose",
    )
    parser.add_argument('--subject', '-s', default="no subject")
    parser.add_argument('recipients', nargs='*')
    parser.add_argument(
        '--message',
        '-m',
        help="read message from filename and not from stdin",
    )
    return parser


def main():
    global VERBOSE
    options = mk_parser().parse_args()
    VERBOSE = options.verbose

    if msg_path := options.message:
        with Path(msg_path).open() as fin:
            raw_email = fin.read()
    else:
        raw_email = sys.stdin.read()
    print(f"{raw_email=}")
    cfg_path = Path(options.config)
    config = load_config(cfg_path)
    print(f"{config}")
    return
    token = get_access_token(config)

    subject, recipients, content_type, content = parse_email_message(raw_email)
    vprint(f"parsed: {(subject, recipients, content_type, content)}")

    recipients = recipients or []
    recipients.extend(fmt_recipients(options.recipients))
    subject = subject or options.subject
    vprint(f"{recipients=}")
    vprint(f"{subject=}")

    if not recipients:
        logger.error("No recipients found in email headers")
        sys.exit(1)

    send_mail(
        token,
        sender=config["from_address"],
        subject=subject,
        recipients=recipients,
        content_type=content_type,
        content=content
    )


if __name__ == '__main__':
    main()
