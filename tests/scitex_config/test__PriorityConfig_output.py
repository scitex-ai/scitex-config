"""Explicit resolution reports preserve masking and survive diagnostic capture."""

import os
import subprocess
import sys
from pathlib import Path

import pytest


def _run(tmp_path, scenario, level, capture):
    import scitex_config

    env = {
        "PATH": str(Path(sys.executable).parent) + os.pathsep + os.defpath,
        "PYTHONPATH": str(Path(scitex_config.__file__).resolve().parents[1]),
        "TMPDIR": str(tmp_path),
        "SCITEX_DIR": str(tmp_path / "state"),
        "XDG_CACHE_HOME": str(tmp_path / "cache"),
        "SCITEX_LOGGING_LEVEL": "CRITICAL",
        "SCITEX_LOGGING_FORCE_COLOR": "0",
        "NO_COLOR": "1",
        "OWNED_REPORT_HOST": "fixture-host",
    }
    script = '''
import json, os, sys
from copy import deepcopy
from pathlib import Path
private = tuple(str(Path.home() / name) for name in ('.scitex', '.claude', '.env'))
def guard(event, args):
    if event in {'socket.bind', 'socket.connect', 'socket.getaddrinfo'}:
        raise RuntimeError('resolution fixtures must remain offline')
    if event in {'open', 'os.listdir', 'os.scandir'} and args:
        if isinstance(args[0], (str, bytes, os.PathLike)):
            path = os.path.abspath(os.fsdecode(args[0]))
            if any(path == root or path.startswith(root + '/') for root in private):
                raise RuntimeError('resolution fixtures forbid personal state')
sys.addaudithook(guard)
import scitex_logging as slogging
from scitex_config import PriorityConfig
scenario, level, capture = sys.argv[1:]
slogging.configure(level=level, enable_file=False, capture_prints=capture == 'yes')
pc = PriorityConfig(config_dict={'port': 4040, 'api_key': 'owned-fixture-value'},
                    env_prefix='OWNED_REPORT_')
if scenario != 'empty':
    assert pc.resolve('port', direct_val=7070, type=int) == 7070
    assert pc.resolve('port', type=int) == 4040
    assert pc.resolve('host') == 'fixture-host'
    assert pc.resolve('missing', default='fixture-default') == 'fixture-default'
    assert pc.resolve('api_key') == 'owned-fixture-value'
if scenario == 'cleared':
    pc.clear_log()
before = deepcopy(pc.resolution_log)
assert pc.print_resolutions() is None
assert pc.resolution_log == before
if scenario == 'repeated':
    assert pc.print_resolutions() is None
    assert pc.resolution_log == before
slogging.getLogger('owned.report.diagnostic').critical('diagnostic-control')
'''
    result = subprocess.run(
        [sys.executable, "-c", script, scenario, level, "yes" if capture else "no"],
        cwd=tmp_path, env=env, capture_output=True, text=True, timeout=30, check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout, result.stderr


@pytest.mark.parametrize("level", ["INFO", "WARNING", "ERROR", "CRITICAL"])
@pytest.mark.parametrize("capture", [False, True])
@pytest.mark.parametrize("scenario", ["empty", "resolved", "cleared", "repeated"])
def test_print_resolutions_preserves_requested_payload(tmp_path, level, capture,
                                                      scenario):
    # Arrange — owned synthetic values only; the API's existing masking is retained.
    entries = [
        ("port", 7070, "direct"), ("port", 4040, "config_dict"),
        ("host", "fixture-host", "env:OWNED_REPORT_HOST"),
        ("missing", "fixture-default", "default"),
        ("api_key", "ow" + "*" * 15 + "ue", "config_dict"),
    ]
    report = "Configuration Resolution Log:\n" + "-" * 50 + "\n"
    report += "".join(f"{key:<20} = {value:<20} ({source})\n"
                      for key, value, source in entries)
    expected = {"empty": "No configurations resolved yet\n",
                "cleared": "No configurations resolved yet\n",
                "resolved": report, "repeated": report * 2}[scenario]
    # Act
    stdout, stderr = _run(tmp_path, scenario, level, capture)
    # Assert
    assert (stdout, stderr, "owned-fixture-value" in stdout) == (
        expected, "CRIT: diagnostic-control\n", False,
    )
