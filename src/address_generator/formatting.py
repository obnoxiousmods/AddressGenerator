"""Formatting helpers for labels, decimals, and output lines."""

from __future__ import annotations

import re
from decimal import ROUND_DOWN, Decimal

from address_generator.models import ReportRow


def sanitize_label(label: str) -> str:
    """Convert a user-supplied label into a stable filesystem-safe form."""

    sanitized = re.sub(r"[^a-zA-Z0-9._-]+", "_", label.strip()).strip("._")
    return sanitized or "scan"


def format_decimal(value: Decimal | None, places: int) -> str:
    """Format a decimal with deterministic truncation."""

    if value is None:
        return "n/a"
    quant = Decimal(1).scaleb(-places)
    return f"{value.quantize(quant, rounding=ROUND_DOWN):f}"


def render_report_row(row: ReportRow, symbol: str) -> str:
    """Render a row into the project text-report format."""

    usd = f" | usd=${format_decimal(row.balance_usd, 2)}" if row.balance_usd is not None else ""
    notes = f" | {' ; '.join(row.notes)}" if row.notes else ""
    return (
        f"index={row.index} | address={row.address} | txs={row.tx_count} "
        f"| balance={format_decimal(row.balance_native, 8)} {symbol}{usd}{notes}"
    )
