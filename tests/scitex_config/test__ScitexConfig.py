#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-12-09"
# File: ./tests/scitex/config/test__ScitexConfig.py

"""Tests for ScitexConfig class and related functions."""

import os
from pathlib import Path
from typing import Iterator

import pytest

from scitex_config import ScitexConfig, get_config, load_yaml


@pytest.fixture
def env_var_guard() -> Iterator[dict]:
    """Snapshot os.environ keys mutated by tests and restore on teardown."""
    # Arrange
    original = dict(os.environ)
    try:
        yield original
    finally:
        # Restore: reset all keys to snapshot state
        for key in list(os.environ):
            if key not in original:
                del os.environ[key]
        for key, value in original.items():
            os.environ[key] = value


def _write_yaml(tmp_path: Path, content: str, name: str = "config.yaml") -> Path:
    """Helper: write a YAML file under tmp_path and return its path."""
    path = tmp_path / name
    path.write_text(content)
    return path


# ----------------------------------------------------------------------------
# load_yaml()
# ----------------------------------------------------------------------------


class TestLoadYaml:
    """Test load_yaml() function."""

    def test_load_yaml_reads_string_value(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "key: value\nnumber: 42\n")
        # Act
        result = load_yaml(path)
        # Assert
        assert result["key"] == "value"

    def test_load_yaml_reads_int_value(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "key: value\nnumber: 42\n")
        # Act
        result = load_yaml(path)
        # Assert
        assert result["number"] == 42

    def test_load_yaml_reads_nested_child_value(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(
            tmp_path, "parent:\n  child: value\n  nested:\n    deep: content\n"
        )
        # Act
        result = load_yaml(path)
        # Assert
        assert result["parent"]["child"] == "value"

    def test_load_yaml_reads_deeply_nested_value(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(
            tmp_path, "parent:\n  child: value\n  nested:\n    deep: content\n"
        )
        # Act
        result = load_yaml(path)
        # Assert
        assert result["parent"]["nested"]["deep"] == "content"

    def test_load_yaml_substitutes_default_when_var_unset(
        self, tmp_path: Path, env_var_guard: dict
    ) -> None:
        """Test ${VAR:-default} syntax substitution."""
        # Arrange
        os.environ.pop("TEST_YAML_VAR", None)
        path = _write_yaml(tmp_path, 'value: ${TEST_YAML_VAR:-"default_value"}\n')
        # Act
        result = load_yaml(path)
        # Assert
        assert result["value"] == "default_value"

    def test_load_yaml_substitutes_env_value_when_var_set(
        self, tmp_path: Path, env_var_guard: dict
    ) -> None:
        # Arrange
        os.environ["TEST_YAML_VAR2"] = "from_env"
        path = _write_yaml(tmp_path, 'value: ${TEST_YAML_VAR2:-"default"}\n')
        # Act
        result = load_yaml(path)
        # Assert
        assert result["value"] == "from_env"

    def test_load_yaml_reads_true_as_python_bool(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "enabled: true\ndisabled: false\n")
        # Act
        result = load_yaml(path)
        # Assert
        assert result["enabled"] is True

    def test_load_yaml_reads_false_as_python_bool(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "enabled: true\ndisabled: false\n")
        # Act
        result = load_yaml(path)
        # Assert
        assert result["disabled"] is False

    def test_load_yaml_raises_value_error_for_nonexistent_file(self) -> None:
        # Arrange
        bad_path = Path("/nonexistent/path/config.yaml")
        # Act
        # Assert
        with pytest.raises(ValueError):
            load_yaml(bad_path)


# ----------------------------------------------------------------------------
# ScitexConfig basics
# ----------------------------------------------------------------------------


class TestScitexConfigBasic:
    """Basic ScitexConfig functionality tests."""

    def test_default_initialization_returns_instance(self) -> None:
        # Arrange
        # Act
        config = ScitexConfig()
        # Assert
        assert config is not None

    def test_custom_config_path_loads_value(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "custom_key: custom_value\n")
        # Act
        config = ScitexConfig(config_path=str(path))
        # Assert
        assert config.get("custom_key") == "custom_value"

    def test_custom_config_path_stored_on_instance(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "custom_key: custom_value\n")
        # Act
        config = ScitexConfig(config_path=str(path))
        # Assert
        assert config.config_path == path

    def test_custom_env_prefix_init_returns_instance(self) -> None:
        # Arrange
        # Act
        config = ScitexConfig(env_prefix="CUSTOM_")
        # Assert
        assert config is not None

    def test_repr_contains_class_name(self) -> None:
        # Arrange
        config = ScitexConfig()
        # Act
        repr_str = repr(config)
        # Assert
        assert "ScitexConfig" in repr_str

    def test_repr_contains_path_keyword(self) -> None:
        # Arrange
        config = ScitexConfig()
        # Act
        repr_str = repr(config)
        # Assert
        assert "path=" in repr_str


# ----------------------------------------------------------------------------
# _flatten_dict (via get)
# ----------------------------------------------------------------------------


class TestScitexConfigFlattenDict:
    """Test dictionary flattening functionality."""

    def test_flat_get_returns_simple_nested_value(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "parent:\n  child: value\n")
        config = ScitexConfig(config_path=str(path))
        # Act
        result = config.get("parent.child")
        # Assert
        assert result == "value"

    def test_flat_get_returns_deeply_nested_value(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "a:\n  b:\n    c:\n      d: deep_value\n")
        config = ScitexConfig(config_path=str(path))
        # Act
        result = config.get("a.b.c.d")
        # Assert
        assert result == "deep_value"


# ----------------------------------------------------------------------------
# get()
# ----------------------------------------------------------------------------


class TestScitexConfigGet:
    """Test get() method."""

    def test_get_returns_value_for_existing_key(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "test_key: test_value\n")
        config = ScitexConfig(config_path=str(path))
        # Act
        result = config.get("test_key")
        # Assert
        assert result == "test_value"

    def test_get_returns_none_for_missing_key_without_default(self) -> None:
        # Arrange
        config = ScitexConfig()
        # Act
        result = config.get("nonexistent_key")
        # Assert
        assert result is None

    def test_get_returns_default_for_missing_key(self) -> None:
        # Arrange
        config = ScitexConfig()
        # Act
        result = config.get("nonexistent_key", default="fallback")
        # Assert
        assert result == "fallback"


# ----------------------------------------------------------------------------
# resolve()
# ----------------------------------------------------------------------------


class TestScitexConfigResolve:
    """Test resolve() method with priority order."""

    def test_resolve_direct_value_beats_config(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "test_key: from_config\n")
        config = ScitexConfig(config_path=str(path))
        # Act
        result = config.resolve(
            "test_key", direct_val="from_direct", default="from_default"
        )
        # Assert
        assert result == "from_direct"

    def test_resolve_config_beats_env_var(
        self, tmp_path: Path, env_var_guard: dict
    ) -> None:
        # Arrange
        os.environ["SCITEX_TEST_KEY"] = "from_env"
        path = _write_yaml(tmp_path, "test_key: from_config\n")
        config = ScitexConfig(config_path=str(path))
        # Act
        result = config.resolve("test_key", default="from_default")
        # Assert
        assert result == "from_config"

    def test_resolve_env_beats_default_when_no_config(
        self, env_var_guard: dict
    ) -> None:
        # Arrange
        os.environ["SCITEX_MISSING_KEY"] = "from_env"
        config = ScitexConfig()
        # Act
        result = config.resolve("missing_key", default="from_default")
        # Assert
        assert result == "from_env"

    def test_resolve_default_used_when_nothing_else_set(self) -> None:
        # Arrange
        config = ScitexConfig()
        # Act
        result = config.resolve("totally_unknown", default="fallback_value")
        # Assert
        assert result == "fallback_value"

    def test_resolve_env_var_converted_to_int_value(self, env_var_guard: dict) -> None:
        # Arrange
        os.environ["SCITEX_INT_VAL"] = "42"
        config = ScitexConfig()
        # Act
        result = config.resolve("int_val", default=0, type=int)
        # Assert
        assert result == 42

    def test_resolve_env_var_int_result_has_int_type(self, env_var_guard: dict) -> None:
        # Arrange
        os.environ["SCITEX_INT_VAL"] = "42"
        config = ScitexConfig()
        # Act
        result = config.resolve("int_val", default=0, type=int)
        # Assert
        assert isinstance(result, int)

    def test_resolve_env_var_converted_to_true_bool(self, env_var_guard: dict) -> None:
        # Arrange
        os.environ["SCITEX_BOOL_VAL"] = "true"
        config = ScitexConfig()
        # Act
        result = config.resolve("bool_val", default=False, type=bool)
        # Assert
        assert result is True


# ----------------------------------------------------------------------------
# get_nested()
# ----------------------------------------------------------------------------


class TestScitexConfigGetNested:
    """Test get_nested() method."""

    def test_get_nested_returns_two_level_value(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "parent:\n  child: nested_value\n")
        config = ScitexConfig(config_path=str(path))
        # Act
        result = config.get_nested("parent", "child")
        # Assert
        assert result == "nested_value"

    def test_get_nested_returns_three_level_value(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "a:\n  b:\n    c: deep\n")
        config = ScitexConfig(config_path=str(path))
        # Act
        result = config.get_nested("a", "b", "c")
        # Assert
        assert result == "deep"

    def test_get_nested_returns_default_for_missing_path(self) -> None:
        # Arrange
        config = ScitexConfig()
        # Act
        result = config.get_nested("missing", "path", default="default_val")
        # Assert
        assert result == "default_val"


# ----------------------------------------------------------------------------
# Properties (raw / flat)
# ----------------------------------------------------------------------------


class TestScitexConfigProperties:
    """Test ScitexConfig properties."""

    @pytest.fixture
    def config_with_parent_child(self, tmp_path: Path) -> ScitexConfig:
        # Arrange
        path = _write_yaml(tmp_path, "parent:\n  child: value\n")
        return ScitexConfig(config_path=str(path))

    def test_raw_property_returns_dict_instance(
        self, config_with_parent_child: ScitexConfig
    ) -> None:
        # Arrange
        # Act
        raw = config_with_parent_child.raw
        # Assert
        assert isinstance(raw, dict)

    def test_raw_property_preserves_top_level_keys(
        self, config_with_parent_child: ScitexConfig
    ) -> None:
        # Arrange
        # Act
        raw = config_with_parent_child.raw
        # Assert
        assert "parent" in raw

    def test_raw_property_preserves_nested_structure(
        self, config_with_parent_child: ScitexConfig
    ) -> None:
        # Arrange
        # Act
        raw = config_with_parent_child.raw
        # Assert
        assert raw["parent"]["child"] == "value"

    def test_flat_property_returns_dict_instance(
        self, config_with_parent_child: ScitexConfig
    ) -> None:
        # Arrange
        # Act
        flat = config_with_parent_child.flat
        # Assert
        assert isinstance(flat, dict)

    def test_flat_property_uses_dot_notation_key(
        self, config_with_parent_child: ScitexConfig
    ) -> None:
        # Arrange
        # Act
        flat = config_with_parent_child.flat
        # Assert
        assert "parent.child" in flat

    def test_flat_property_dot_key_maps_to_leaf_value(
        self, config_with_parent_child: ScitexConfig
    ) -> None:
        # Arrange
        # Act
        flat = config_with_parent_child.flat
        # Assert
        assert flat["parent.child"] == "value"


# ----------------------------------------------------------------------------
# get_config()
# ----------------------------------------------------------------------------


class TestGetConfig:
    """Test get_config() convenience function."""

    def test_get_config_returns_scitex_config_instance(self) -> None:
        # Arrange
        # Act
        config = get_config()
        # Assert
        assert isinstance(config, ScitexConfig)

    def test_get_config_loads_value_from_custom_path(self, tmp_path: Path) -> None:
        # Arrange
        path = _write_yaml(tmp_path, "custom: value\n")
        # Act
        config = get_config(config_path=str(path))
        # Assert
        assert config.get("custom") == "value"


if __name__ == "__main__":
    import pytest as _pytest

    _pytest.main([os.path.abspath(__file__)])
