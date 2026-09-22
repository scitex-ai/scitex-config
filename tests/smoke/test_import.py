"""Smoke: installed package imports and resolves a default (PS-211).

Subprocess-driven (``sys.executable -c ...``) so this proves the installed
distribution resolves — an in-process import would not. Hermetic: no
network, no credentials, no writes outside tmp dirs.
"""

from __future__ import annotations

import subprocess
import sys

import pytest

pytestmark = pytest.mark.smoke


def test_import_and_resolve_default_subprocess() -> None:
    # Arrange
    argv = [
        sys.executable,
        "-c",
        "import scitex_config as cfg; "
        "print(cfg.PriorityConfig().resolve('missing.key', default='dflt'))",
    ]
    # Act
    completed = subprocess.run(argv, capture_output=True, text=True, timeout=30)
    # Assert
    assert (completed.returncode, completed.stdout.strip()) == (0, "dflt")
