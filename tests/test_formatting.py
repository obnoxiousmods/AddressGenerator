from __future__ import annotations

from decimal import Decimal

from address_generator.formatting import format_decimal, render_report_row, sanitize_label
from address_generator.models import ReportRow


def test_sanitize_label() -> None:
    assert sanitize_label(" hello world ") == "hello_world"


def test_format_decimal_handles_none() -> None:
    assert format_decimal(None, 2) == "n/a"


def test_render_report_row() -> None:
    row = ReportRow(
        index=1,
        address="abc",
        tx_count=2,
        balance_native=Decimal("1.25"),
        balance_usd=Decimal("10"),
    )
    assert (
        render_report_row(row, "BTC")
        == "index=1 | address=abc | txs=2 | balance=1.25000000 BTC | usd=$10.00"
    )
