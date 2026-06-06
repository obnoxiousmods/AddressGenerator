"""Configuration loading for TOML and dictionary-based scans."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any, cast

from address_generator.exceptions import ConfigurationError
from address_generator.formatting import sanitize_label
from address_generator.models import (
    ChainSymbol,
    InputMode,
    OutputFormat,
    ScanRequest,
    ScanTarget,
)


def load_scan_request(path: Path, output_dir: Path | None = None) -> ScanRequest:
    """Load a ``ScanRequest`` from a TOML file."""

    return parse_scan_request_data(
        tomllib.loads(path.read_text(encoding="utf-8")),
        output_dir=output_dir,
    )


def parse_scan_request_data(data: Mapping[str, Any], output_dir: Path | None = None) -> ScanRequest:
    """Parse a mapping into a typed ``ScanRequest``."""

    defaults = cast_mapping(data.get("defaults", {}))
    try:
        label = sanitize_label(str(data["label"]))
        max_count = int(data.get("max_count", defaults.get("max_count", 25)))
        raw_targets = data["targets"]
    except KeyError as exc:
        msg = f"Missing required config key: {exc.args[0]}"
        raise ConfigurationError(msg) from exc

    formats = parse_formats(data.get("formats", defaults.get("formats", ["txt", "json"])))
    targets = tuple(_parse_target(item, defaults) for item in raw_targets)
    if not targets:
        raise ConfigurationError("Configuration must contain at least one target.")

    return ScanRequest(
        label=label,
        max_count=max_count,
        targets=targets,
        output_dir=output_dir or Path("output"),
        formats=formats,
    )


def parse_formats(raw: object) -> tuple[OutputFormat, ...]:
    """Parse output formats from config or CLI values."""

    if isinstance(raw, str):
        items = [part.strip() for part in raw.split(",") if part.strip()]
    elif isinstance(raw, list):
        items = [str(part).strip() for part in raw if str(part).strip()]
    else:
        raise ConfigurationError("formats must be a string or list of strings.")
    if not items:
        raise ConfigurationError("At least one output format is required.")
    return tuple(OutputFormat(item.lower()) for item in items)


def _parse_target(item: object, defaults: Mapping[str, Any]) -> ScanTarget:
    """Parse a single TOML target table into a typed target."""

    if not isinstance(item, Mapping):
        raise ConfigurationError("Each target must be a TOML table.")
    mapping = cast_mapping(item)

    try:
        chain = ChainSymbol(str(mapping["chain"]).upper())
        mode = InputMode(str(mapping.get("mode", defaults.get("mode", "addresses"))).lower())
        value = str(mapping["value"]).strip()
    except KeyError as exc:
        msg = f"Target is missing required key: {exc.args[0]}"
        raise ConfigurationError(msg) from exc

    raw_branches = mapping.get("branches", defaults.get("branches", [0]))
    branches = tuple(int(item) for item in raw_branches)
    raw_providers = mapping.get("providers", defaults.get("providers", []))
    provider_order = tuple(str(item) for item in raw_providers)
    count = mapping.get("count")
    return ScanTarget(
        chain=chain,
        mode=mode,
        value=value,
        count=None if count is None else int(count),
        branches=branches,
        provider_order=provider_order,
        label=None if mapping.get("label") is None else str(mapping["label"]),
    )


def cast_mapping(item: object) -> Mapping[str, Any]:
    """Narrow a dynamic mapping into a string-keyed mapping."""

    if not isinstance(item, Mapping):
        raise ConfigurationError("Expected a mapping structure.")
    return cast(Mapping[str, Any], item)
