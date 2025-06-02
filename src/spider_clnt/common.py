import json

from pathlib import Path


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
