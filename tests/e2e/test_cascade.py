"""E2E: real priority cascade — direct > config_dict > env > default (PS-212).

Drives the real ``PriorityConfig`` against a real process env var and a
real config dict. No network, loopback-only by construction (pure memory).

No monkeypatch (PA-306): explicit save/restore with try/finally.
"""

from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.e2e

from scitex_config import PriorityConfig


def test_direct_beats_config_dict_env_default() -> None:
    # Arrange
    pc = PriorityConfig(
        config_dict={"service.port": 8080},
        env_prefix="E2E_SCITEX_",
    )
    os.environ["E2E_SCITEX_SERVICE_PORT"] = "9090"
    try:
        # Act
        value = pc.resolve("service.port", direct_val=7070, type=int)
    finally:
        os.environ.pop("E2E_SCITEX_SERVICE_PORT", None)
    # Assert
    assert value == 7070


def test_config_dict_beats_env() -> None:
    # Arrange
    pc = PriorityConfig(
        config_dict={"service.port": 8080},
        env_prefix="E2E_SCITEX_",
    )
    os.environ["E2E_SCITEX_SERVICE_PORT"] = "9090"
    try:
        # Act
        value = pc.resolve("service.port", type=int)
    finally:
        os.environ.pop("E2E_SCITEX_SERVICE_PORT", None)
    # Assert
    assert value == 8080


def test_env_beats_default() -> None:
    # Arrange
    pc = PriorityConfig(env_prefix="E2E_SCITEX_")
    os.environ["E2E_SCITEX_SERVICE_HOST"] = "env-host"
    try:
        # Act
        value = pc.resolve("service.host", default="dflt-host")
    finally:
        os.environ.pop("E2E_SCITEX_SERVICE_HOST", None)
    # Assert
    assert value == "env-host"


def test_default_used_when_nothing_set() -> None:
    # Arrange
    pc = PriorityConfig(env_prefix="E2E_SCITEX_")
    # Act
    value = pc.resolve("service.missing", default="dflt")
    # Assert
    assert value == "dflt"
