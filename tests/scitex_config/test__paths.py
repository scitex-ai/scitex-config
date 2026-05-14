#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-09"
# File: ./tests/scitex/config/test__paths.py

"""Tests for ScitexPaths class and get_paths() function."""

import os
from pathlib import Path
from typing import Iterator

import pytest

from scitex_config import ScitexPaths, get_paths


@pytest.fixture
def scitex_dir_guard() -> Iterator[None]:
    """Snapshot SCITEX_DIR and restore it on teardown."""
    # Arrange
    original = os.environ.get("SCITEX_DIR")
    try:
        yield
    finally:
        if original is None:
            os.environ.pop("SCITEX_DIR", None)
        else:
            os.environ["SCITEX_DIR"] = original


@pytest.fixture
def paths(tmp_path: Path) -> ScitexPaths:
    """ScitexPaths instance rooted at a fresh tmp_path."""
    # Arrange
    return ScitexPaths(base_dir=str(tmp_path))


# ----------------------------------------------------------------------------
# Initialisation
# ----------------------------------------------------------------------------


class TestScitexPathsBasic:
    """Basic ScitexPaths functionality tests."""

    def test_default_initialization_returns_non_none_instance(
        self, scitex_dir_guard: None
    ) -> None:
        # Arrange
        os.environ.pop("SCITEX_DIR", None)
        # Act
        result = ScitexPaths()
        # Assert
        assert result is not None

    def test_default_initialization_uses_home_dot_scitex(
        self, scitex_dir_guard: None
    ) -> None:
        # Arrange
        os.environ.pop("SCITEX_DIR", None)
        # Act
        result = ScitexPaths()
        # Assert
        assert result.base == Path.home() / ".scitex"

    def test_explicit_base_dir_overrides_env(self, tmp_path: Path) -> None:
        # Arrange
        # Act
        result = ScitexPaths(base_dir=str(tmp_path))
        # Assert
        assert result.base == tmp_path

    def test_initialization_reads_scitex_dir_env_var(
        self, tmp_path: Path, scitex_dir_guard: None
    ) -> None:
        # Arrange
        os.environ["SCITEX_DIR"] = str(tmp_path)
        # Act
        result = ScitexPaths()
        # Assert
        assert result.base == tmp_path

    def test_repr_contains_class_name(self, paths: ScitexPaths) -> None:
        # Arrange
        # Act
        repr_str = repr(paths)
        # Assert
        assert "ScitexPaths" in repr_str

    def test_repr_contains_base_keyword(self, paths: ScitexPaths) -> None:
        # Arrange
        # Act
        repr_str = repr(paths)
        # Assert
        assert "base=" in repr_str


# ----------------------------------------------------------------------------
# Core directory properties
# ----------------------------------------------------------------------------


class TestScitexPathsCoreDirectories:
    """Test core directory properties."""

    def test_logs_path_is_base_slash_logs(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.logs == tmp_path / "logs"

    def test_cache_path_is_base_slash_cache(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.cache == tmp_path / "cache"

    def test_capture_path_is_base_slash_capture(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.capture == tmp_path / "capture"

    def test_screenshots_path_is_base_slash_screenshots(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.screenshots == tmp_path / "screenshots"

    def test_rng_path_is_base_slash_rng(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.rng == tmp_path / "rng"


class TestScitexPathsBrowserDirectories:
    """Test browser-related directory properties."""

    def test_browser_path_is_base_slash_browser(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.browser == tmp_path / "browser"

    def test_browser_screenshots_nested_under_browser(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.browser_screenshots == tmp_path / "browser" / "screenshots"

    def test_browser_sessions_nested_under_browser(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.browser_sessions == tmp_path / "browser" / "sessions"

    def test_browser_persistent_nested_under_browser(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.browser_persistent == tmp_path / "browser" / "persistent"

    def test_test_monitor_path_is_base_slash_test_monitor(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.test_monitor == tmp_path / "test_monitor"


class TestScitexPathsCacheDirectories:
    """Test cache-related directory properties."""

    def test_function_cache_nested_under_cache(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.function_cache == tmp_path / "cache" / "functions"

    def test_impact_factor_cache_is_base_slash_impact_factor_cache(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.impact_factor_cache == tmp_path / "impact_factor_cache"

    def test_openathens_cache_is_base_slash_openathens_cache(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.openathens_cache == tmp_path / "openathens_cache"


class TestScitexPathsScholarDirectories:
    """Test scholar-related directory properties."""

    def test_scholar_path_is_base_slash_scholar(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.scholar == tmp_path / "scholar"

    def test_scholar_cache_nested_under_scholar(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.scholar_cache == tmp_path / "scholar" / "cache"

    def test_scholar_library_nested_under_scholar(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.scholar_library == tmp_path / "scholar" / "library"


class TestScitexPathsWriterDirectories:
    """Test writer-related directory properties."""

    def test_writer_path_is_base_slash_writer(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert paths.writer == tmp_path / "writer"


# ----------------------------------------------------------------------------
# resolve()
# ----------------------------------------------------------------------------


class TestScitexPathsResolve:
    """Test resolve() method."""

    def test_resolve_returns_direct_value_when_provided(
        self, paths: ScitexPaths
    ) -> None:
        # Arrange
        custom_path = "/custom/cache/path"
        # Act
        result = paths.resolve("cache", direct_val=custom_path)
        # Assert
        assert result == Path(custom_path)

    def test_resolve_returns_default_when_direct_val_none(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        result = paths.resolve("cache", direct_val=None)
        # Assert
        assert result == tmp_path / "cache"

    def test_resolve_expands_tilde_to_home(self, paths: ScitexPaths) -> None:
        # Arrange
        # Act
        result = paths.resolve("logs", direct_val="~/custom_logs")
        # Assert
        assert "~" not in str(result)

    def test_resolve_expanded_path_starts_at_home(self, paths: ScitexPaths) -> None:
        # Arrange
        # Act
        result = paths.resolve("logs", direct_val="~/custom_logs")
        # Assert
        assert str(result).startswith(str(Path.home()))

    @pytest.mark.parametrize("name", ["logs", "cache", "browser", "scholar", "writer"])
    def test_resolve_returns_path_instance_for_known_name(
        self, paths: ScitexPaths, name: str
    ) -> None:
        # Arrange
        # Act
        result = paths.resolve(name)
        # Assert
        assert isinstance(result, Path)

    def test_resolve_raises_value_error_for_unknown_path_name(
        self, paths: ScitexPaths
    ) -> None:
        # Arrange
        # Act
        # Assert
        with pytest.raises(ValueError):
            paths.resolve("unknown_path_name")

    def test_resolve_value_error_message_mentions_unknown_path_name(
        self, paths: ScitexPaths
    ) -> None:
        # Arrange
        # Act
        try:
            paths.resolve("unknown_path_name")
            message = ""
        except ValueError as exc:
            message = str(exc)
        # Assert
        assert "Unknown path name" in message


# ----------------------------------------------------------------------------
# ensure_dir / ensure_all
# ----------------------------------------------------------------------------


class TestScitexPathsEnsureDir:
    """Test ensure_dir() method."""

    def test_ensure_dir_creates_missing_directory_on_disk(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        new_dir = tmp_path / "new_subdir"
        # Act
        paths.ensure_dir(new_dir)
        # Assert
        assert new_dir.exists()

    def test_ensure_dir_returns_input_path(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        new_dir = tmp_path / "another_subdir"
        # Act
        result = paths.ensure_dir(new_dir)
        # Assert
        assert result == new_dir

    def test_ensure_dir_is_idempotent_on_existing_directory(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        # Act
        result = paths.ensure_dir(tmp_path)
        # Assert
        assert result == tmp_path

    def test_ensure_dir_creates_nested_parent_directories(
        self, paths: ScitexPaths, tmp_path: Path
    ) -> None:
        # Arrange
        nested_dir = tmp_path / "a" / "b" / "c"
        # Act
        paths.ensure_dir(nested_dir)
        # Assert
        assert nested_dir.exists()


class TestScitexPathsEnsureAll:
    """Test ensure_all() method."""

    @pytest.fixture
    def ensured_paths(self, paths: ScitexPaths) -> ScitexPaths:
        # Arrange / Act
        paths.ensure_all()
        return paths

    def test_ensure_all_creates_logs_directory(
        self, ensured_paths: ScitexPaths
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert ensured_paths.logs.exists()

    def test_ensure_all_creates_cache_directory(
        self, ensured_paths: ScitexPaths
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert ensured_paths.cache.exists()

    def test_ensure_all_creates_browser_directory(
        self, ensured_paths: ScitexPaths
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert ensured_paths.browser.exists()

    def test_ensure_all_creates_scholar_directory(
        self, ensured_paths: ScitexPaths
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert ensured_paths.scholar.exists()

    def test_ensure_all_creates_writer_directory(
        self, ensured_paths: ScitexPaths
    ) -> None:
        # Arrange
        # Act
        # Assert
        assert ensured_paths.writer.exists()


# ----------------------------------------------------------------------------
# list_all
# ----------------------------------------------------------------------------


_EXPECTED_LIST_ALL_KEYS = [
    "base",
    "logs",
    "cache",
    "function_cache",
    "capture",
    "screenshots",
    "rng",
    "browser",
    "browser_screenshots",
    "browser_sessions",
    "browser_persistent",
    "test_monitor",
    "impact_factor_cache",
    "openathens_cache",
    "scholar",
    "scholar_cache",
    "scholar_library",
    "writer",
]


class TestScitexPathsListAll:
    """Test list_all() method."""

    def test_list_all_returns_a_dict(self, paths: ScitexPaths) -> None:
        # Arrange
        # Act
        result = paths.list_all()
        # Assert
        assert isinstance(result, dict)

    @pytest.mark.parametrize("key", _EXPECTED_LIST_ALL_KEYS)
    def test_list_all_contains_expected_key(self, paths: ScitexPaths, key: str) -> None:
        # Arrange
        # Act
        result = paths.list_all()
        # Assert
        assert key in result, f"Missing key: {key}"

    def test_list_all_values_are_path_instances(self, paths: ScitexPaths) -> None:
        # Arrange
        result = paths.list_all()
        # Act
        non_paths = [k for k, v in result.items() if not isinstance(v, Path)]
        # Assert
        assert non_paths == []


# ----------------------------------------------------------------------------
# get_paths
# ----------------------------------------------------------------------------


class TestGetPaths:
    """Test get_paths() convenience function."""

    def test_get_paths_returns_scitex_paths_instance(self) -> None:
        # Arrange
        # Act
        result = get_paths()
        # Assert
        assert isinstance(result, ScitexPaths)

    def test_get_paths_honours_custom_base_dir(self, tmp_path: Path) -> None:
        # Arrange
        # Act
        result = get_paths(base_dir=str(tmp_path))
        # Assert
        assert result.base == tmp_path

    def test_get_paths_returns_scitex_paths_on_repeated_no_arg_call(self) -> None:
        """get_paths() with no args should keep returning a ScitexPaths instance."""
        # Arrange
        get_paths()
        # Act
        second = get_paths()
        # Assert
        assert isinstance(second, ScitexPaths)


if __name__ == "__main__":
    import pytest as _pytest

    _pytest.main([os.path.abspath(__file__)])
