"""Resolution reports accept the same values as the dictionary resolver."""

from copy import deepcopy

import pytest

from scitex_config import PriorityConfig


CASES = [
    pytest.param(
        source, value,
        {"direct": {}, "config_dict": {"selection": value}, "default": {}}[source],
        {"direct": {"direct_val": value}, "config_dict": {}, "default": {"default": value}}[source],
        id=f"{source}-{label}",
    )
    for source in ("direct", "config_dict", "default")
    for label, value in (
        ("list", ["alpha", "beta"]),
        ("dict", {"nested": [1, 2]}),
        ("none", None),
        ("false", False),
        ("integer", 42),
        ("string", "unchanged"),
    )
    if not (source == "direct" and value is None)
]


@pytest.mark.parametrize("source,value,config_values,options", CASES)
def test_report_displays_resolved_value_without_mutating_it(
    source, value, config_values, options, capsys
):
    # Arrange
    config = PriorityConfig(config_dict=config_values, env_prefix="OWNED_REPORT_")
    resolved = config.resolve("selection", **options)
    before = deepcopy(config.resolution_log)
    # Act
    config.print_resolutions()
    captured = capsys.readouterr()
    # Assert
    assert (
        resolved is value,
        config.resolution_log == before,
        f"{'selection':<20} = {str(value):<20} ({source})" in captured.out,
        captured.err,
    ) == (True, True, True, "")


@pytest.mark.parametrize("value", [{"token": "owned-private-report-sentinel"}, None])
def test_report_preserves_sensitive_masking_and_resolved_value(value, capsys):
    # Arrange
    config = PriorityConfig(config_dict={"api_key": value}, env_prefix="OWNED_REPORT_")
    resolved = config.resolve("api_key")
    before = deepcopy(config.resolution_log)
    # Act
    config.print_resolutions()
    captured = capsys.readouterr()
    # Assert
    assert (
        resolved is value,
        config.resolution_log == before,
        "owned-private-report-sentinel" not in captured.out + captured.err,
        str(before[0]["value"]) in captured.out,
        "(config_dict)" in captured.out,
    ) == (True, True, True, True, True)


def test_empty_resolution_report_keeps_its_message(capsys):
    # Arrange
    config = PriorityConfig(env_prefix="OWNED_REPORT_")
    # Act
    config.print_resolutions()
    captured = capsys.readouterr()
    # Assert
    assert (captured.out, captured.err) == ("No configurations resolved yet\n", "")
