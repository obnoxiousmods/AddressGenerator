from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
from typing import cast

import pytest
from rich.console import Console

from address_generator import cli
from address_generator.app import AddressGeneratorApp
from address_generator.models import ChainSymbol, InputMode, ScanRequest, ScanTarget


def test_build_scan_request_from_flags() -> None:
    args = cli.build_parser().parse_args(
        [
            "scan",
            "--label",
            "demo",
            "--count",
            "3",
            "--chain",
            "BTC",
            "--mode",
            "addresses",
            "--value",
            "a\nb\nc",
            "--branches",
            "0,1",
            "--provider",
            "blockstream-public",
            "--format",
            "txt,csv",
        ]
    )
    request = cli._build_scan_request(args, Console(file=StringIO()))
    assert request.label == "demo"
    assert request.max_count == 3
    assert request.targets[0].branches == (0, 1)
    assert request.targets[0].provider_order == ("blockstream-public",)
    assert tuple(item.value for item in request.formats) == ("txt", "csv")


@pytest.mark.parametrize(
    ("argv", "helper_name"),
    [
        (["address-generator", "providers"], "_run_providers"),
        (["address-generator", "derive", "--chain", "BTC", "--xpub", "xpub"], "_run_derive"),
        (
            [
                "address-generator",
                "validate",
                "--chain",
                "ETH",
                "--mode",
                "addresses",
                "--value",
                "0xabc",
            ],
            "_run_validate",
        ),
        (["address-generator", "tui"], "_run_tui"),
    ],
)
def test_main_dispatches_subcommands(
    monkeypatch: pytest.MonkeyPatch,
    argv: list[str],
    helper_name: str,
) -> None:
    called: list[str] = []

    class FakeApp:
        pass

    def fake_create_default() -> FakeApp:
        return FakeApp()

    def fake_helper(*args: object, **kwargs: object) -> None:
        del args, kwargs
        called.append(helper_name)

    monkeypatch.setattr(cli.AddressGeneratorApp, "create_default", fake_create_default)
    monkeypatch.setattr(cli, helper_name, fake_helper)
    monkeypatch.setattr("sys.argv", argv)

    cli.main()

    assert called == [helper_name]


def test_run_derive_json_prints_payload() -> None:
    class FakeApp:
        def derive_entries(
            self,
            chain: ChainSymbol,
            public_key: str,
            branches: tuple[int, ...],
            count: int,
        ) -> list[object]:
            del chain, public_key, branches, count
            return [
                type(
                    "Entry",
                    (),
                    {"branch": 0, "index": 0, "path_label": "0/0", "address": "bc1qexample"},
                )(),
            ]

    buffer = StringIO()
    console = Console(file=buffer, force_terminal=False, color_system=None)
    args = cli.build_parser().parse_args(
        ["derive", "--chain", "BTC", "--xpub", "xpub", "--json"]
    )
    cli._run_derive(cast(AddressGeneratorApp, FakeApp()), console, args)
    payload = json.loads(buffer.getvalue())
    assert payload[0]["address"] == "bc1qexample"


def test_run_providers_csv_prints_catalog(provider_catalog: object) -> None:
    class FakeApp:
        def __init__(self, provider_catalog: object) -> None:
            self.provider_catalog = provider_catalog

    buffer = StringIO()
    console = Console(file=buffer, force_terminal=False, color_system=None)
    cli._run_providers(
        cast(AddressGeneratorApp, FakeApp(provider_catalog)),
        console,
        as_json=False,
        as_csv=True,
    )
    output = buffer.getvalue()
    assert "provider_id" in output
    assert "ethplorer" in output


def test_run_validate_for_addresses_uses_loader() -> None:
    class FakeApp:
        def load_addresses(self, value: str, count: int) -> list[str]:
            assert value == "a\nb"
            assert count == 2
            return ["a", "b"]

    buffer = StringIO()
    console = Console(file=buffer, force_terminal=False, color_system=None)
    args = cli.build_parser().parse_args(
        [
            "validate",
            "--chain",
            "ETH",
            "--mode",
            "addresses",
            "--value",
            "a\nb",
            "--count",
            "2",
        ]
    )
    cli._run_validate(cast(AddressGeneratorApp, FakeApp()), console, args)
    assert "loaded 2 address(es)" in buffer.getvalue()


def test_run_tui_uses_config(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
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
    captured: list[ScanRequest] = []

    class FakeRunner:
        def __init__(self, app: object) -> None:
            del app

        def run(self, request: ScanRequest) -> None:
            captured.append(request)

    monkeypatch.setattr(cli, "TuiRunner", FakeRunner)
    args = cli.build_parser().parse_args(["tui", "--config", str(config_path)])
    cli._run_tui(cast(AddressGeneratorApp, object()), args)
    assert captured[0].label == "demo"


def test_run_tui_uses_interactive_without_config(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[Path] = []

    class FakeRunner:
        def __init__(self, app: object) -> None:
            del app

        def run_interactive(self, output_dir: Path) -> None:
            captured.append(output_dir)

    monkeypatch.setattr(cli, "TuiRunner", FakeRunner)
    args = cli.build_parser().parse_args(["tui"])
    cli._run_tui(cast(AddressGeneratorApp, object()), args)
    assert captured == [Path("output")]


def test_main_scan_prints_output_path(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: list[ScanRequest] = []

    class FakeApp:
        def run(self, request: ScanRequest) -> object:
            captured.append(request)
            return type("Result", (), {"output_dir": Path("out/demo")})()

    def fake_create_default() -> FakeApp:
        return FakeApp()

    monkeypatch.setattr(cli.AddressGeneratorApp, "create_default", fake_create_default)
    monkeypatch.setattr(
        "sys.argv",
        [
            "address-generator",
            "scan",
            "--chain",
            "ETH",
            "--mode",
            "addresses",
            "--value",
            "0xabc",
        ],
    )
    cli.main()
    assert captured[0].targets == (
        ScanTarget(chain=ChainSymbol.ETH, mode=InputMode.ADDRESSES, value="0xabc"),
    )
