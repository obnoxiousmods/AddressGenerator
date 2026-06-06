"""Configuration loading for TOML-based scans."""

from __future__ import annotations

import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from address_generator.exceptions import ConfigurationError
from address_generator.formatting import sanitize_label
from address_generator.models import ChainSymbol, InputMode, ScanRequest, ScanTarget


def load_scan_request(path: Path, output_dir: Path | None = None) -> ScanRequest:
    """Load a ``ScanRequest`` from a TOML file."""

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    try:
        label = sanitize_label(str(data["label"]))
        max_count = int(data["max_count"])
        raw_targets = data["targets"]
    except KeyError as exc:
        msg = f"Missing required config key: {exc.args[0]}"
        raise ConfigurationError(msg) from exc

    targets = tuple(_parse_target(item) for item in raw_targets)
    if not targets:
        raise ConfigurationError("Configuration must contain at least one target.")

    return ScanRequest(
        label=label,
        max_count=max_count,
        targets=targets,
        output_dir=output_dir or Path("output"),
    )


def _parse_target(item: object) -> ScanTarget:
    """Parse a single TOML target table into a typed target."""

    if not isinstance(item, Mapping):
        raise ConfigurationError("Each target must be a TOML table.")
    mapping = cast_mapping(item)

    try:
        chain = ChainSymbol(str(mapping["chain"]).upper())
        mode = InputMode(str(mapping["mode"]).lower())
        value = str(mapping["value"]).strip()
    except KeyError as exc:
        msg = f"Target is missing required key: {exc.args[0]}"
        raise ConfigurationError(msg) from exc
    return ScanTarget(chain=chain, mode=mode, value=value)


def cast_mapping(item: Mapping[Any, Any]) -> Mapping[str, Any]:
    """Narrow a dynamic TOML mapping into a string-keyed mapping."""

    return item
