#!/usr/bin/env python

# #############################################################################
# Copyright : (C) 2024 by MHComm. All rights reserved
#
# Name       :  spider_clnt.commands.spdrmta
"""
  Summary : command line mta to send mails

__author__ = "Klaus Foerster"
__email__ = "info@mhcomm.fr"

Simple MTA that sends mails via spider API
"""
# #############################################################################
import argparse
import logging
import os
import sys

from pathlib import Path

import spider_clnt.common as common

from spider_clnt.common import load_config
from spider_clnt.common import vprint
from spider_clnt.client import SpiderClient
from spider_clnt.client import fmt_recipients
from spider_clnt.client import parse_email_message


logger = logging.getLogger(__name__)


def mk_parser():
    """ commandline parser """
    description = "no description given"
    default_cfg = str(common.CONFIG_PATH)
    default_cfg = os.environ.get("SPIDER_CLNT_CONFIG", default_cfg)
    verbose_char = os.environ.get("SPDRMTA_VERBOSE", "false")[:1].lower()
    verbose = verbose_char in ("1", "t")
    debug = os.environ.get("SPDRMTA_DEBUG", "false")[:1].lower() in ("1", "t")

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
        default=verbose,
        help="be a little more verbose default=%(default)s",
    )
    parser.add_argument(
        '--debug',
        '-d',
        action="store_true",
        default=debug,
        help="activate debug info default=%(default)s",
    )
    parser.add_argument('--from-email', '-f')
    parser.add_argument('--subject', '-s', default="no subject")
    parser.add_argument('recipients', nargs='*')
    parser.add_argument(
        '--message',
        '-m',
        help="read message from filename and not from stdin",
    )
    return parser


def main():
    options = mk_parser().parse_args()
    common.VERBOSE = options.verbose
    common.DEBUG = options.debug

    if msg_path := options.message:
        with Path(msg_path).open() as fin:
            raw_email = fin.read()
    else:
        raw_email = sys.stdin.read()
    print(f"{raw_email=}")
    cfg_path = Path(options.config)
    config = load_config(cfg_path)
    print(f"{config}")
    client = SpiderClient(**config)
    if options.from_email:
        assert options.from_email == client.sender
    client.login()

    subject, recipients, content_type, content = parse_email_message(raw_email)
    vprint(f"parsed: {(subject, recipients, content_type, content)}")

    recipients = recipients or []
    recipients.extend(fmt_recipients(options.recipients))
    recipients = set(recipients)

    subject = subject or options.subject
    vprint(f"{recipients=}")
    vprint(f"{subject=}")

    if not recipients:
        logger.error("No recipients found in email headers")
        sys.exit(1)

    result = client.send_mail(
        sender=config["sender"],
        subject=subject,
        recipients=recipients,
        content_type=content_type,
        content=content
    )
    vprint(f"{result=}")
    # return client, result (if somebody wants to call and check results)
    return client, result


if __name__ == '__main__':
    main()
