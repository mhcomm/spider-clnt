#!/usr/bin/env python

# #############################################################################
# Copyright : (C) 2024 by MHComm. All rights reserved
#
# Name       :  spider_clnt.commands.spdrsms
"""
  Summary : command line tool to send SMS

__author__ = "Klaus Foerster"
__email__ = "info@mhcomm.fr"

Simple script that sends SMS via spider API
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


logger = logging.getLogger(__name__)


def mk_parser():
    """ commandline parser """
    description = "no description given"
    default_cfg = str(common.CONFIG_PATH)
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
    parser.add_argument('recipient')
    parser.add_argument(
        '--message',
        '-m',
        help="read message from filename and not from stdin",
    )
    return parser


def main():
    options = mk_parser().parse_args()
    common.VERBOSE = options.verbose

    if msg_path := options.message:
        with Path(msg_path).open() as fin:
            raw_sms = fin.read()
    else:
        raw_sms = sys.stdin.read()
    print(f"{raw_sms=}")
    content = raw_sms
    cfg_path = Path(options.config)
    config = load_config(cfg_path)
    print(f"{config}")
    cfg = dict(config)
    cfg.pop("sender")
    client = SpiderClient(**cfg)
    client.login()

    recipient = options.recipients
    vprint(f"{recipient=}")

    result = client.send_sms(
        sender=config["sms_sender"],
        recipient=recipient,
        content=content,
    )
    vprint(f"{result=}")
    # return client, result (if somebody wants to call and check results)
    return client, result


if __name__ == '__main__':
    main()
