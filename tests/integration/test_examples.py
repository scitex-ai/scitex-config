"""Smoke tests: every example script must run to completion."""

import subprocess
import sys
from pathlib import Path

import pytest

EXAMPLES = list(Path(__file__).parents[2].joinpath("examples").glob("*.py"))


def test_examples_directory_contains_scripts():
    # Arrange
    # Act
    # Assert
    assert EXAMPLES, "no example scripts found"


@pytest.mark.parametrize("example_path", EXAMPLES, ids=lambda p: p.name)
def test_example_script_exits_with_zero_returncode(example_path, tmp_path):
    # Arrange
    # Act
    r = subprocess.run(
        [sys.executable, str(example_path)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=60,
    )
    # Assert
    assert r.returncode == 0, f"{example_path.name} failed: {r.stderr}"
