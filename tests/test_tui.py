from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from io import StringIO
from pathlib import Path
from typing import cast

import pytest
from rich.console import Console

from address_generator.app import AddressGeneratorApp
from address_generator.models import ChainSymbol, InputMode, ReportRow, ScanRequest, ScanTarget
from address_generator.tui import TuiRunner


class FakeReportWriter:
    def build_output_dir(self, base_output_dir: Path, label: str) -> Path:
        return base_output_dir / label


class FakeApp:
    def __init__(self) -> None:
        self.report_writer = FakeReportWriter()
        self.ran = False

    def run_with_progress(
        self,
        request: ScanRequest,
        progress: Callable[[ChainSymbol, int, int, ReportRow | None], None],
    ) -> object:
        self.ran = True
        assert request.label == "demo"
        assert callable(progress)
        progress(
            ChainSymbol.BTC,
            1,
            1,
            ReportRow(
                index=0,
                address="bc1qexample",
                tx_count=1,
                balance_native=Decimal("0"),
                provider_id="blockstream-public",
            ),
        )
        return object()


def test_tui_runner_runs_request() -> None:
    app = FakeApp()
    buffer = StringIO()
    console = Console(file=buffer, force_terminal=False, color_system=None)
    request = ScanRequest(
        label="demo",
        max_count=1,
        output_dir=Path("out"),
        targets=(ScanTarget(chain=ChainSymbol.BTC, mode=InputMode.ADDRESSES, value="bc1"),),
    )
    TuiRunner(app=cast(AddressGeneratorApp, app), console=console).run(request)
    assert app.ran is True
    assert "Output written to out/demo" in buffer.getvalue()


def test_tui_runner_interactive_calls_builder(monkeypatch: pytest.MonkeyPatch) -> None:
    app = FakeApp()
    console = Console(file=StringIO(), force_terminal=False, color_system=None)
    captured: list[Path] = []

    class FakeBuilder:
        def __init__(self, console: Console) -> None:
            del console

        def build(self, output_dir: Path) -> ScanRequest:
            captured.append(output_dir)
            return ScanRequest(
                label="demo",
                max_count=1,
                output_dir=output_dir,
                targets=(
                    ScanTarget(chain=ChainSymbol.BTC, mode=InputMode.ADDRESSES, value="bc1"),
                ),
            )

    monkeypatch.setattr("address_generator.tui.InteractiveRequestBuilder", FakeBuilder)
    TuiRunner(app=cast(AddressGeneratorApp, app), console=console).run_interactive(Path("out"))
    assert captured == [Path("out")]
