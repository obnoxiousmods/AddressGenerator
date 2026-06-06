from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from address_generator.app import AddressGeneratorApp
from address_generator.models import (
    ChainRunResult,
    ChainSymbol,
    InputMode,
    ReportRow,
    RunResult,
    ScanRequest,
    ScanSummary,
    ScanTarget,
)


class FakeScanService:
    def build_rows(self, target: ScanTarget, max_count: int) -> tuple[ReportRow, ...]:
        assert max_count == 2
        if target.chain is ChainSymbol.BTC:
            return (
                ReportRow(
                    index=0,
                    address="bc1",
                    tx_count=1,
                    balance_native=Decimal("0"),
                ),
            )
        raise RuntimeError("boom")

    def summarize_rows(self, rows: tuple[ReportRow, ...]) -> ScanSummary:
        return ScanSummary(
            total_count=1,
            active_count=1,
            total_native_balance=Decimal("0"),
            total_usd_value=Decimal("0"),
        )


class FakeReportWriter:
    def __init__(self) -> None:
        self.written: RunResult | None = None

    def build_output_dir(self, base_output_dir: Path, label: str) -> Path:
        return base_output_dir / label

    def write(self, result: RunResult) -> None:
        self.written = result


def test_app_collects_success_and_failure() -> None:
    writer = FakeReportWriter()
    app = AddressGeneratorApp(scan_service=FakeScanService(), report_writer=writer)  # type: ignore[arg-type]
    request = ScanRequest(
        label="demo",
        max_count=2,
        targets=(
            ScanTarget(chain=ChainSymbol.BTC, mode=InputMode.ADDRESSES, value="bc1"),
            ScanTarget(chain=ChainSymbol.ETH, mode=InputMode.ADDRESSES, value="0xabc"),
        ),
        output_dir=Path("out"),
    )

    result = app.run(request)

    assert writer.written is result
    assert result.chains[ChainSymbol.BTC].summary is not None
    assert result.chains[ChainSymbol.ETH].error == "boom"
    assert isinstance(result.chains[ChainSymbol.BTC], ChainRunResult)
