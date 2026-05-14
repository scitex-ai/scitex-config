"""Tests for scitex_config._ecosystem.local_state — per-package path resolver."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterator

import pytest

from scitex_config._ecosystem import local_state


@pytest.fixture
def env_guard() -> Iterator[None]:
    """Snapshot HOME / SCITEX_DIR / cwd and restore on teardown.

    Lets individual tests mutate these via os.environ / os.chdir without
    leaking across tests (replaces monkeypatch).
    """
    # Arrange
    snapshot = {
        "HOME": os.environ.get("HOME"),
        "SCITEX_DIR": os.environ.get("SCITEX_DIR"),
    }
    cwd = os.getcwd()
    try:
        yield
    finally:
        for key, value in snapshot.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        try:
            os.chdir(cwd)
        except FileNotFoundError:
            os.chdir(Path.home())


@pytest.fixture
def isolated_home(tmp_path: Path, env_guard: None, request) -> Path:
    """Override $HOME and $SCITEX_DIR so tests don't touch the user's
    real ~/.scitex/ tree. Returns the fake $SCITEX_DIR root.

    Only chdir's to fake_home if `fake_repo` is NOT also being used by
    the test (so the two fixtures compose without trampling cwd)."""
    # Arrange
    fake_home = tmp_path / "fake-home"
    fake_home.mkdir(exist_ok=True)
    fake_scitex = tmp_path / "fake-scitex"
    os.environ["HOME"] = str(fake_home)
    os.environ["SCITEX_DIR"] = str(fake_scitex)
    if "fake_repo" not in request.fixturenames:
        os.chdir(fake_home)
    return fake_scitex


@pytest.fixture
def fake_repo(tmp_path: Path, env_guard: None) -> Path:
    """Create a tmp dir with a `.git/` marker so find_project_scope
    treats it as a repo root. cwd is set inside it."""
    # Arrange
    repo = tmp_path / "myproj"
    repo.mkdir()
    (repo / ".git").mkdir()
    os.chdir(repo)
    return repo


def test_user_root_default_uses_home_dot_scitex(
    tmp_path: Path, env_guard: None
) -> None:
    # Arrange
    fake_home = tmp_path / "h"
    fake_home.mkdir()
    os.environ["HOME"] = str(fake_home)
    os.environ.pop("SCITEX_DIR", None)
    # Act
    result = local_state.user_root()
    # Assert
    assert result == fake_home / ".scitex"


def test_user_root_honours_scitex_dir_env(tmp_path: Path, env_guard: None) -> None:
    # Arrange
    custom = tmp_path / "custom-scitex"
    os.environ["SCITEX_DIR"] = str(custom)
    # Act
    result = local_state.user_root()
    # Assert
    assert result == custom


def test_user_root_resolved_live_per_call(tmp_path: Path, env_guard: None) -> None:
    """Live env changes take effect mid-process."""
    # Arrange
    os.environ["SCITEX_DIR"] = str(tmp_path / "first")
    first = local_state.user_root()
    os.environ["SCITEX_DIR"] = str(tmp_path / "second")
    # Act
    second = local_state.user_root()
    # Assert
    assert first != second


def test_find_project_scope_returns_none_outside_repo(isolated_home: Path) -> None:
    # Arrange
    # Act
    result = local_state.find_project_scope("hpc")
    # Assert
    assert result is None


def test_find_project_scope_returns_none_when_dir_missing(fake_repo: Path) -> None:
    """Repo exists but no `.scitex/<pkg>/` — returns None."""
    # Arrange
    # Act
    result = local_state.find_project_scope("hpc")
    # Assert
    assert result is None


def test_find_project_scope_finds_existing_pkg_dir(fake_repo: Path) -> None:
    # Arrange
    scope = fake_repo / ".scitex" / "hpc"
    scope.mkdir(parents=True)
    # Act
    result = local_state.find_project_scope("hpc")
    # Assert
    assert result == scope


def test_find_project_scope_walks_up_from_subdir(
    fake_repo: Path, env_guard: None
) -> None:
    """cwd deep inside the repo still finds the scope at repo root."""
    # Arrange
    scope = fake_repo / ".scitex" / "hpc"
    scope.mkdir(parents=True)
    deep = fake_repo / "a" / "b" / "c"
    deep.mkdir(parents=True)
    os.chdir(deep)
    # Act
    result = local_state.find_project_scope("hpc")
    # Assert
    assert result == scope


def test_path_falls_back_to_user_when_no_repo(isolated_home: Path) -> None:
    """No repo around → resolve to $SCITEX_DIR/<pkg>/<sub>."""
    # Arrange
    # Act
    p = local_state.path("hpc", "config.yaml")
    # Assert
    assert p == isolated_home / "hpc" / "config.yaml"


def test_path_falls_back_when_project_scope_lacks_file(
    fake_repo: Path, isolated_home: Path
) -> None:
    """Project-scope dir exists but file inside doesn't — fall back to user scope."""
    # Arrange
    (fake_repo / ".scitex" / "hpc").mkdir(parents=True)
    # Act
    p = local_state.path("hpc", "config.yaml")
    # Assert
    assert p == isolated_home / "hpc" / "config.yaml"


def test_path_uses_project_scope_when_file_exists(
    fake_repo: Path, isolated_home: Path
) -> None:
    """File exists in project scope — that wins."""
    # Arrange
    project = fake_repo / ".scitex" / "hpc"
    project.mkdir(parents=True)
    project_file = project / "config.yaml"
    project_file.write_text("project_scope: true\n")
    # Act
    result = local_state.path("hpc", "config.yaml")
    # Assert
    assert result == project_file


def test_user_path_skips_project_scope_for_existing_file(
    fake_repo: Path, isolated_home: Path
) -> None:
    """user_path always returns user-scope path even when project scope has the file."""
    # Arrange
    project = fake_repo / ".scitex" / "hpc"
    project.mkdir(parents=True)
    (project / "host-id.yaml").write_text("project: yes\n")
    # Act
    p = local_state.user_path("hpc", "host-id.yaml")
    # Assert
    assert p == isolated_home / "hpc" / "host-id.yaml"


@pytest.fixture
def runtime_path_user_first_call(isolated_home: Path) -> tuple[Path, Path]:
    """Trigger runtime_path() once in user scope and return (log, dir)."""
    # Arrange
    log = local_state.runtime_path("hpc", "dispatch.log")
    runtime_dir = isolated_home / "hpc" / "runtime"
    return log, runtime_dir


def test_runtime_path_creates_runtime_dir_in_user_scope(
    runtime_path_user_first_call: tuple[Path, Path],
) -> None:
    # Arrange
    _, runtime_dir = runtime_path_user_first_call
    # Act
    # Assert
    assert runtime_dir.is_dir()


def test_runtime_path_creates_gitkeep_in_user_scope(
    runtime_path_user_first_call: tuple[Path, Path],
) -> None:
    # Arrange
    _, runtime_dir = runtime_path_user_first_call
    # Act
    # Assert
    assert (runtime_dir / ".gitkeep").exists()


def test_runtime_path_creates_readme_in_user_scope(
    runtime_path_user_first_call: tuple[Path, Path],
) -> None:
    # Arrange
    _, runtime_dir = runtime_path_user_first_call
    # Act
    # Assert
    assert (runtime_dir / "README.md").exists()


def test_runtime_path_returns_file_inside_runtime_dir(
    runtime_path_user_first_call: tuple[Path, Path],
) -> None:
    # Arrange
    log, runtime_dir = runtime_path_user_first_call
    # Act
    # Assert
    assert log == runtime_dir / "dispatch.log"


@pytest.fixture
def runtime_path_project_first_call(fake_repo: Path) -> tuple[Path, Path]:
    """Trigger runtime_path() once in project scope and return (log, dir)."""
    # Arrange
    (fake_repo / ".scitex" / "hpc").mkdir(parents=True)
    log = local_state.runtime_path("hpc", "dispatch.log")
    runtime_dir = fake_repo / ".scitex" / "hpc" / "runtime"
    return log, runtime_dir


def test_runtime_path_creates_runtime_dir_in_project_scope(
    runtime_path_project_first_call: tuple[Path, Path],
) -> None:
    """If project scope is active, seeds land there."""
    # Arrange
    _, runtime_dir = runtime_path_project_first_call
    # Act
    # Assert
    assert runtime_dir.is_dir()


def test_runtime_path_creates_gitkeep_in_project_scope(
    runtime_path_project_first_call: tuple[Path, Path],
) -> None:
    # Arrange
    _, runtime_dir = runtime_path_project_first_call
    # Act
    # Assert
    assert (runtime_dir / ".gitkeep").exists()


def test_runtime_path_creates_readme_in_project_scope(
    runtime_path_project_first_call: tuple[Path, Path],
) -> None:
    # Arrange
    _, runtime_dir = runtime_path_project_first_call
    # Act
    # Assert
    assert (runtime_dir / "README.md").exists()


def test_runtime_path_returns_file_under_project_runtime(
    runtime_path_project_first_call: tuple[Path, Path],
) -> None:
    # Arrange
    log, runtime_dir = runtime_path_project_first_call
    # Act
    # Assert
    assert log == runtime_dir / "dispatch.log"


def test_runtime_path_is_idempotent_for_custom_readme(isolated_home: Path) -> None:
    """Calling runtime_path twice doesn't clobber a customized README."""
    # Arrange
    runtime_dir = isolated_home / "hpc" / "runtime"
    runtime_dir.mkdir(parents=True)
    (runtime_dir / "README.md").write_text("custom content\n")
    # Act
    local_state.runtime_path("hpc")
    # Assert
    assert (runtime_dir / "README.md").read_text() == "custom content\n"


def test_path_with_no_parts_returns_pkg_root(isolated_home: Path) -> None:
    # Arrange
    # Act
    result = local_state.path("hpc")
    # Assert
    assert result == isolated_home / "hpc"


def test_user_path_with_no_parts_returns_pkg_root(isolated_home: Path) -> None:
    # Arrange
    # Act
    result = local_state.user_path("hpc")
    # Assert
    assert result == isolated_home / "hpc"


def test_runtime_path_with_no_parts_returns_runtime_dir(isolated_home: Path) -> None:
    # Arrange
    # Act
    rt = local_state.runtime_path("hpc")
    # Assert
    assert rt == isolated_home / "hpc" / "runtime"
