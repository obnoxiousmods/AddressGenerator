from __future__ import annotations

from pathlib import Path

import pytest

from address_generator.config import load_scan_request
from address_generator.exceptions import ConfigurationError
from address_generator.models import ChainSymbol, InputMode, OutputFormat


def test_load_scan_request(tmp_path: Path) -> None:
    config_path = tmp_path / "scan.toml"
    config_path.write_text(
        """
label = " example "
max_count = 2

[[targets]]
chain = "btc"
mode = "xpub"
value = "abc"
""",
        encoding="utf-8",
    )

    request = load_scan_request(config_path)

    assert request.label == "example"
    assert request.max_count == 2
    assert request.targets[0].chain is ChainSymbol.BTC
    assert request.targets[0].mode is InputMode.XPUB


def test_load_scan_request_rejects_missing_keys(tmp_path: Path) -> None:
    config_path = tmp_path / "scan.toml"
    config_path.write_text('label = "oops"\n', encoding="utf-8")

    with pytest.raises(ConfigurationError):
        load_scan_request(config_path)


def test_load_scan_request_parses_defaults_and_formats(tmp_path: Path) -> None:
    config_path = tmp_path / "scan.toml"
    config_path.write_text(
        """
label = "demo"
formats = ["txt", "csv"]

[defaults]
branches = [0, 1]

[[targets]]
chain = "doge"
mode = "addresses"
value = "Dabc"
""",
        encoding="utf-8",
    )
    request = load_scan_request(config_path)
    assert request.formats == (OutputFormat.TXT, OutputFormat.CSV)
    assert request.targets[0].branches == (0, 1)
