import json

from pathlib import Path


CONFIG_PATH = Path.home() / ".config" / "spider_clnt.json"
LOG_PATH = Path.home() / "spider_clnt.log"
VERBOSE = False
DEBUG = False


def vprint(*args, **kwargs):
    """
    print if verbose
    """
    if VERBOSE:
        print(*args, **kwargs)
    if DEBUG:
        try:
            with LOG_PATH.open("a") as fout:
                print(*args, **kwargs, file=fout)
        except Exception:
            print("e", end=".")


def load_config(configfile):
    """
    load spider_clnt config file
    """
    cfg_path = Path(configfile)
    with cfg_path.open() as fin:
        data = json.load(fin)
        entry = data["default"]
        return {
            "url": entry["url"],
            "username": entry["username"],
            "password": entry["password"],
            "sender": entry["sender"],
            # "client_id": entry["application_id"],
            # "client_secret": entry["secret_value"],
            # "from_address": entry["sender"],
        }
