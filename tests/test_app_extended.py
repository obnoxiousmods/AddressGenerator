from __future__ import annotations

from collections.abc import Callable
from decimal import Decimal
from pathlib import Path

from address_generator.app import AddressGeneratorApp
from address_generator.models import (
    ChainSymbol,
    InputMode,
    ReportRow,
    ScanRequest,
    ScanSummary,
    ScanTarget,
)


class RecordingScanService:
    def __init__(self) -> None:
        self.progress_events: list[tuple[ChainSymbol, int, int, ReportRow | None]] = []

    def build_rows(
        self,
        target: ScanTarget,
        max_count: int,
        *,
        progress: Callable[[ChainSymbol, int, int, ReportRow | None], None] | None = None,
    ) -> tuple[ReportRow, ...]:
        assert max_count == 2
        row = ReportRow(
            index=0,
            address=target.value,
            tx_count=1,
            balance_native=Decimal("1"),
            provider_id="ethplorer",
        )
        if callable(progress):
            progress(target.chain, 1, 1, row)
        return (row,)

    def summarize_rows(self, rows: tuple[ReportRow, ...]) -> ScanSummary:
        return ScanSummary(
            total_count=len(rows),
            active_count=len(rows),
            total_native_balance=Decimal("1"),
            total_usd_value=Decimal("10"),
        )


class RecordingWriter:
    def __init__(self) -> None:
        self.written: object | None = None

    def build_output_dir(self, base_output_dir: Path, label: str) -> Path:
        return base_output_dir / label

    def write(self, result: object) -> None:
        self.written = result


def test_create_default_exposes_helpers() -> None:
    app = AddressGeneratorApp.create_default()
    addresses = app.load_addresses("a,b", 2)
    assert addresses == ["a", "b"]
    assert len(app.provider_catalog.list_metadata()) >= 4


def test_run_with_progress_records_callback() -> None:
    writer = RecordingWriter()
    app = AddressGeneratorApp.create_default()
    custom = AddressGeneratorApp(
        scan_service=RecordingScanService(),
        report_writer=writer,
        provider_catalog=app.provider_catalog,
        address_deriver=app.address_deriver,
        address_input_loader=app.address_input_loader,
    )
    request = ScanRequest(
        label="demo",
        max_count=2,
        output_dir=Path("out"),
        targets=(ScanTarget(chain=ChainSymbol.ETH, mode=InputMode.ADDRESSES, value="0xabc"),),
    )
    events: list[tuple[ChainSymbol, int, int, ReportRow | None]] = []
    result = custom.run_with_progress(request, lambda *args: events.append(args))
    assert writer.written is result
    assert events[0][0] is ChainSymbol.ETH
    assert result.chains[ChainSymbol.ETH].providers_tried == ("ethplorer",)


def test_derive_entries_facade() -> None:
    app = AddressGeneratorApp.create_default()
    entries = app.derive_entries(
        ChainSymbol.BTC,
        (
            "zpub6rFR7y4Q2AijBEqTUquhVz398htDFrtymD9xYYfG1m4wAcvPhXNfE3EfH1r1"
            "ADqtfSdVCToUG868RvUUkgDKf31mGDtKsAYz2oz2AGutZYs"
        ),
        (0,),
        1,
    )
    assert len(entries) == 1
    assert entries[0].path_label == "0/0"
