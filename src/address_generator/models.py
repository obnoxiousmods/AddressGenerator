"""Typed domain models for scan requests and results."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from pathlib import Path


class ChainSymbol(StrEnum):
    """Supported chain identifiers."""

    BTC = "BTC"
    LTC = "LTC"
    DOGE = "DOGE"
    ETH = "ETH"


class InputMode(StrEnum):
    """How a target provides public wallet data."""

    XPUB = "xpub"
    ADDRESSES = "addresses"


@dataclass(frozen=True)
class ScanTarget:
    """One chain-specific public input to scan."""

    chain: ChainSymbol
    mode: InputMode
    value: str


@dataclass(frozen=True)
class ScanRequest:
    """Top-level request describing a full reporting run."""

    label: str
    max_count: int
    targets: tuple[ScanTarget, ...]
    output_dir: Path = Path("output")


@dataclass(frozen=True)
class ReportRow:
    """One address report row."""

    index: int | str
    address: str
    tx_count: int
    balance_native: Decimal
    balance_usd: Decimal | None = None
    notes: tuple[str, ...] = ()

    @property
    def is_active(self) -> bool:
        """Return whether the row should appear in the active-only report."""

        return self.tx_count > 0 or self.balance_native > 0 or bool(self.notes)


@dataclass(frozen=True)
class ScanSummary:
    """Aggregate results for one scanned chain."""

    total_count: int
    active_count: int
    total_native_balance: Decimal
    total_usd_value: Decimal


@dataclass(frozen=True)
class ChainRunResult:
    """Detailed result for a single chain."""

    rows: tuple[ReportRow, ...]
    summary: ScanSummary | None = None
    error: str | None = None


@dataclass(frozen=True)
class RunResult:
    """Result for a full project run."""

    output_dir: Path
    chains: dict[ChainSymbol, ChainRunResult] = field(default_factory=dict)
