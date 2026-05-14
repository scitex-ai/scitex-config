"""Compile-only stub for examples/quickstart.py (PS303)."""

import subprocess
import sys
from pathlib import Path

import pytest

QUICKSTART = Path(__file__).parents[2] / "examples" / "quickstart.py"


@pytest.fixture
def quickstart_compile_result() -> subprocess.CompletedProcess:
    # Arrange
    assert QUICKSTART.is_file(), f"missing {QUICKSTART}"
    # Act
    return subprocess.run(
        [sys.executable, "-m", "py_compile", str(QUICKSTART)],
        capture_output=True,
        text=True,
    )


def test_quickstart_script_file_exists_on_disk():
    # Arrange
    # Act
    # Assert
    assert QUICKSTART.is_file(), f"missing {QUICKSTART}"


def test_quickstart_script_compiles_without_syntax_errors(
    quickstart_compile_result: subprocess.CompletedProcess,
) -> None:
    # Arrange
    # Act
    # Assert
    assert quickstart_compile_result.returncode == 0
