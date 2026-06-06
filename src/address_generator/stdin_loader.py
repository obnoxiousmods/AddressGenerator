"""Helpers for building scan requests from stdin payloads."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from address_generator.config import parse_formats, parse_scan_request_data
from address_generator.models import ChainSymbol, InputMode, ScanRequest, ScanTarget, StdinFormat


def load_request_from_stdin(
    payload: str,
    *,
    stdin_format: StdinFormat,
    output_dir: Path,
    label: str | None = None,
    max_count: int = 25,
    chain: ChainSymbol | None = None,
    mode: InputMode | None = None,
    formats: tuple[str, ...] = ("txt", "json"),
) -> ScanRequest:
    """Build a scan request from stdin data."""

    if stdin_format is StdinFormat.JSON:
        return parse_scan_request_data(json.loads(payload), output_dir=output_dir)
    if stdin_format is StdinFormat.TOML:
        return parse_scan_request_data(tomllib.loads(payload), output_dir=output_dir)

    assert chain is not None
    selected_mode = mode or InputMode.ADDRESSES
    target = ScanTarget(chain=chain, mode=selected_mode, value=payload.strip())
    return ScanRequest(
        label=label or "stdin-scan",
        max_count=max_count,
        targets=(target,),
        output_dir=output_dir,
        formats=parse_formats(list(formats)),
    )
