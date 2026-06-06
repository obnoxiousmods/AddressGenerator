from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from address_generator.models import (
    ChainRunResult,
    ChainSymbol,
    OutputFormat,
    ReportRow,
    RunResult,
    ScanSummary,
)
from address_generator.reporting import ReportWriter


def test_report_writer_writes_expected_files(tmp_path: Path) -> None:
    writer = ReportWriter()
    output_dir = tmp_path / "demo"
    rows = (
        ReportRow(index=0, address="a", tx_count=1, balance_native=Decimal("1")),
        ReportRow(index=1, address="b", tx_count=0, balance_native=Decimal("0")),
    )
    result = RunResult(
        output_dir=output_dir,
        formats=(OutputFormat.TXT, OutputFormat.JSON, OutputFormat.CSV),
        chains={
            ChainSymbol.BTC: ChainRunResult(
                rows=rows,
                summary=ScanSummary(
                    total_count=2,
                    active_count=1,
                    total_native_balance=Decimal("1"),
                    total_usd_value=Decimal("10"),
                ),
            )
        },
    )

    writer.write(result)

    assert (output_dir / "BTC_all.txt").exists()
    assert (output_dir / "BTC_active.txt").exists()
    assert (output_dir / "BTC_all.json").exists()
    assert (output_dir / "BTC_all.csv").exists()
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["chains"]["BTC"]["active_count"] == 1


def test_report_writer_handles_error_summary(tmp_path: Path) -> None:
    writer = ReportWriter()
    result = RunResult(
        output_dir=tmp_path / "demo",
        chains={ChainSymbol.ETH: ChainRunResult(rows=(), error="failed")},
    )
    writer.write(result)
    summary = json.loads((result.output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["chains"]["ETH"]["error"] == "failed"
