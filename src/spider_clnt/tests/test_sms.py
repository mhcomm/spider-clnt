import sys

from pathlib import Path
from unittest.mock import patch

import pytest

import spider_clnt.commands.spdrsms as spdrsms


def mk_args(*args):
    """
    make sys.argv arguments
    """
    newargs = [
        str(Path(spdrsms.__file__).resolve())
    ] + list(args)
    return newargs


def test_show_help(capsys):
    """
    can help be displayed
    """
    newargs = mk_args("-h")
    print(f"{newargs}")
    with patch.object(sys, "argv", newargs):
        with pytest.raises(SystemExit):
            spdrsms.main()
        captured = capsys.readouterr().out
        with capsys.disabled():
            print(captured)
        assert "usage: spdrsms" in captured
