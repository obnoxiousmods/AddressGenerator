from __future__ import annotations

from pathlib import Path

import pytest

from address_generator import cli
from address_generator.models import ScanRequest


def test_build_parser_defaults() -> None:
    parser = cli.build_parser()
    args = parser.parse_args([])
    assert args.config is None
    assert args.output_dir == Path("output")


def test_cli_main_uses_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    config_path = tmp_path / "scan.toml"
    config_path.write_text(
        """
label = "demo"
max_count = 1

[[targets]]
chain = "ETH"
mode = "addresses"
value = "0xabc"
""",
        encoding="utf-8",
    )

    captured: dict[str, ScanRequest] = {}

    class FakeApp:
        def run(self, request: ScanRequest) -> object:
            captured["request"] = request
            return type("Result", (), {"output_dir": tmp_path / "out"})()

    def fake_create_default() -> FakeApp:
        return FakeApp()

    monkeypatch.setattr(cli.AddressGeneratorApp, "create_default", fake_create_default)
    monkeypatch.setattr("sys.argv", ["address-generator", "--config", str(config_path)])

    cli.main()

    assert captured["request"].label == "demo"
