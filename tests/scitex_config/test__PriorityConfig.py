#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-09"
# File: ./tests/scitex/config/test__PriorityConfig.py

"""Tests for PriorityConfig class and load_dotenv, get_scitex_dir functions."""

import os
from pathlib import Path
from typing import Iterator

import pytest

from scitex_config import PriorityConfig, get_scitex_dir, load_dotenv


@pytest.fixture
def env_var_guard() -> Iterator[None]:
    """Snapshot os.environ and restore on teardown."""
    # Arrange
    original = dict(os.environ)
    try:
        yield
    finally:
        for key in list(os.environ):
            if key not in original:
                del os.environ[key]
        for key, value in original.items():
            os.environ[key] = value


# ----------------------------------------------------------------------------
# Basic init / repr
# ----------------------------------------------------------------------------


class TestPriorityConfigBasic:
    """Basic PriorityConfig functionality tests."""

    def test_default_initialization_returns_instance(self) -> None:
        # Arrange
        # Act
        config = PriorityConfig()
        # Assert
        assert config is not None

    def test_config_dict_init_get_returns_stored_value(self) -> None:
        # Arrange
        # Act
        config = PriorityConfig(config_dict={"port": 3000})
        # Assert
        assert config.get("port") == 3000

    def test_env_prefix_init_stores_prefix_on_instance(self) -> None:
        # Arrange
        # Act
        config = PriorityConfig(env_prefix="TEST_")
        # Assert
        assert config.env_prefix == "TEST_"

    def test_repr_contains_env_prefix(self) -> None:
        # Arrange
        config = PriorityConfig(config_dict={"a": 1, "b": 2}, env_prefix="APP_")
        # Act
        repr_str = repr(config)
        # Assert
        assert "APP_" in repr_str

    def test_repr_contains_config_dict_size(self) -> None:
        # Arrange
        config = PriorityConfig(config_dict={"a": 1, "b": 2}, env_prefix="APP_")
        # Act
        repr_str = repr(config)
        # Assert
        assert "2" in repr_str


# ----------------------------------------------------------------------------
# resolve() precedence
# ----------------------------------------------------------------------------


class TestPriorityConfigResolution:
    """Test priority resolution order: direct → config_dict → env → default."""

    def test_resolve_direct_value_beats_config_dict(self) -> None:
        # Arrange
        config = PriorityConfig(config_dict={"port": 3000}, env_prefix="TEST_")
        # Act
        result = config.resolve("port", direct_val=9000, default=8000)
        # Assert
        assert result == 9000

    def test_resolve_config_dict_beats_env_var(self, env_var_guard: None) -> None:
        # Arrange
        os.environ["TEST_PORT"] = "5000"
        config = PriorityConfig(config_dict={"port": 3000}, env_prefix="TEST_")
        # Act
        result = config.resolve("port", default=8000)
        # Assert
        assert result == 3000

    def test_resolve_env_var_beats_default(self, env_var_guard: None) -> None:
        # Arrange
        os.environ["TEST_HOST"] = "localhost"
        config = PriorityConfig(env_prefix="TEST_")
        # Act
        result = config.resolve("host", default="0.0.0.0")
        # Assert
        assert result == "localhost"

    def test_resolve_falls_back_to_default(self) -> None:
        # Arrange
        config = PriorityConfig(env_prefix="TEST_")
        # Act
        result = config.resolve("unknown_key", default="fallback")
        # Assert
        assert result == "fallback"


# ----------------------------------------------------------------------------
# Type conversion
# ----------------------------------------------------------------------------


class TestPriorityConfigTypeConversion:
    """Test type conversion in resolve()."""

    def test_int_type_returns_correct_int_value(self, env_var_guard: None) -> None:
        # Arrange
        os.environ["TEST_COUNT"] = "42"
        config = PriorityConfig(env_prefix="TEST_")
        # Act
        result = config.resolve("count", default=0, type=int)
        # Assert
        assert result == 42

    def test_int_type_returns_int_instance(self, env_var_guard: None) -> None:
        # Arrange
        os.environ["TEST_COUNT"] = "42"
        config = PriorityConfig(env_prefix="TEST_")
        # Act
        result = config.resolve("count", default=0, type=int)
        # Assert
        assert isinstance(result, int)

    def test_float_type_returns_correct_float_value(self, env_var_guard: None) -> None:
        # Arrange
        os.environ["TEST_RATE"] = "3.14"
        config = PriorityConfig(env_prefix="TEST_")
        # Act
        result = config.resolve("rate", default=0.0, type=float)
        # Assert
        assert result == 3.14

    @pytest.mark.parametrize("true_val", ["true", "1", "yes"])
    def test_bool_type_returns_true_for_truthy_string(
        self, env_var_guard: None, true_val: str
    ) -> None:
        # Arrange
        os.environ["TEST_DEBUG"] = true_val
        config = PriorityConfig(env_prefix="TEST_")
        # Act
        result = config.resolve("debug", default=False, type=bool)
        # Assert
        assert result is True

    def test_list_type_splits_comma_separated_string(self, env_var_guard: None) -> None:
        # Arrange
        os.environ["TEST_ITEMS"] = "a,b,c"
        config = PriorityConfig(env_prefix="TEST_")
        # Act
        result = config.resolve("items", default=[], type=list)
        # Assert
        assert result == ["a", "b", "c"]


# ----------------------------------------------------------------------------
# Sensitive value masking
# ----------------------------------------------------------------------------


class TestPriorityConfigSensitiveValues:
    """Test sensitive value masking."""

    def test_sensitive_key_logged_value_is_masked(self) -> None:
        # Arrange
        config = PriorityConfig(config_dict={"api_key": "secret123"})
        # Act
        config.resolve("api_key", default="")
        log_entry = config.resolution_log[0]
        # Assert
        assert log_entry["value"] != "secret123"

    def test_mask_false_disables_sensitive_masking(self) -> None:
        # Arrange
        config = PriorityConfig(config_dict={"api_key": "secret123"})
        # Act
        config.resolve("api_key", default="", mask=False)
        log_entry = config.resolution_log[0]
        # Assert
        assert log_entry["value"] == "secret123"


# ----------------------------------------------------------------------------
# load_dotenv()
# ----------------------------------------------------------------------------


class TestLoadDotenv:
    """Test load_dotenv() function."""

    def test_load_dotenv_returns_true_for_explicit_path(
        self, tmp_path: Path, env_var_guard: None
    ) -> None:
        # Arrange
        path = tmp_path / ".env"
        path.write_text("TEST_DOTENV_VAR=explicit_value\n")
        os.environ.pop("TEST_DOTENV_VAR", None)
        # Act
        result = load_dotenv(str(path))
        # Assert
        assert result is True

    def test_load_dotenv_sets_env_var_from_explicit_path(
        self, tmp_path: Path, env_var_guard: None
    ) -> None:
        # Arrange
        path = tmp_path / ".env"
        path.write_text("TEST_DOTENV_VAR=explicit_value\n")
        os.environ.pop("TEST_DOTENV_VAR", None)
        # Act
        load_dotenv(str(path))
        # Assert
        assert os.environ.get("TEST_DOTENV_VAR") == "explicit_value"

    def test_load_dotenv_returns_false_for_nonexistent_path(self) -> None:
        # Arrange
        # Act
        result = load_dotenv("/nonexistent/path/.env")
        # Assert
        assert result is False

    def test_load_dotenv_skips_comment_lines_when_parsing(
        self, tmp_path: Path, env_var_guard: None
    ) -> None:
        """Test load_dotenv skips comment lines."""
        # Arrange
        path = tmp_path / ".env"
        path.write_text("# Comment\nTEST_COMMENT_VAR=value\n")
        os.environ.pop("TEST_COMMENT_VAR", None)
        # Act
        load_dotenv(str(path))
        # Assert
        assert os.environ.get("TEST_COMMENT_VAR") == "value"

    def test_load_dotenv_strips_export_prefix(
        self, tmp_path: Path, env_var_guard: None
    ) -> None:
        # Arrange
        path = tmp_path / ".env"
        path.write_text("export TEST_EXPORT_VAR=exported_value\n")
        os.environ.pop("TEST_EXPORT_VAR", None)
        # Act
        load_dotenv(str(path))
        # Assert
        assert os.environ.get("TEST_EXPORT_VAR") == "exported_value"

    def test_load_dotenv_strips_surrounding_double_quotes(
        self, tmp_path: Path, env_var_guard: None
    ) -> None:
        # Arrange
        path = tmp_path / ".env"
        path.write_text('TEST_QUOTE_VAR="quoted value"\n')
        os.environ.pop("TEST_QUOTE_VAR", None)
        # Act
        load_dotenv(str(path))
        # Assert
        assert os.environ.get("TEST_QUOTE_VAR") == "quoted value"

    def test_load_dotenv_preserves_existing_env_var(
        self, tmp_path: Path, env_var_guard: None
    ) -> None:
        """Test load_dotenv does not override existing env vars."""
        # Arrange
        path = tmp_path / ".env"
        path.write_text("TEST_EXISTING_VAR=from_dotenv\n")
        os.environ["TEST_EXISTING_VAR"] = "from_shell"
        # Act
        load_dotenv(str(path))
        # Assert
        assert os.environ.get("TEST_EXISTING_VAR") == "from_shell"


# ----------------------------------------------------------------------------
# get_scitex_dir()
# ----------------------------------------------------------------------------


class TestGetScitexDir:
    """Test get_scitex_dir() function."""

    def test_default_value_is_home_dot_scitex(self, env_var_guard: None) -> None:
        # Arrange
        os.environ.pop("SCITEX_DIR", None)
        # Act
        result = get_scitex_dir()
        # Assert
        assert result == Path.home() / ".scitex"

    def test_env_var_overrides_default_path(
        self, tmp_path: Path, env_var_guard: None
    ) -> None:
        # Arrange
        os.environ["SCITEX_DIR"] = str(tmp_path)
        # Act
        result = get_scitex_dir()
        # Assert
        assert result == tmp_path

    def test_direct_val_overrides_env_var(
        self, tmp_path: Path, env_var_guard: None
    ) -> None:
        # Arrange
        env_dir = tmp_path / "env"
        direct_dir = tmp_path / "direct"
        env_dir.mkdir()
        direct_dir.mkdir()
        os.environ["SCITEX_DIR"] = str(env_dir)
        # Act
        result = get_scitex_dir(direct_val=str(direct_dir))
        # Assert
        assert result == direct_dir

    def test_direct_val_with_tilde_expands_to_home(self) -> None:
        # Arrange
        # Act
        result = get_scitex_dir(direct_val="~/custom_scitex")
        # Assert
        assert "~" not in str(result)


if __name__ == "__main__":
    import pytest as _pytest

    _pytest.main([os.path.abspath(__file__)])
