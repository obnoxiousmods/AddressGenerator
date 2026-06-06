"""Typed domain models for scan requests and results."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from pathlib import Path


class ChainSymbol(StrEnum):
    """Supported chain identifiers."""

    BTC = "BTC"
    BCH = "BCH"
    LTC = "LTC"
    DOGE = "DOGE"
    ZEC = "ZEC"
    ETH = "ETH"
    ETC = "ETC"
    POL = "POL"
    BSC = "BSC"
    ARB = "ARB"
    BASE = "BASE"
    OP = "OP"


class InputMode(StrEnum):
    """How a target provides public wallet data."""

    XPUB = "xpub"
    ADDRESSES = "addresses"


class OutputFormat(StrEnum):
    """Supported report output formats."""

    TXT = "txt"
    JSON = "json"
    CSV = "csv"


class StdinFormat(StrEnum):
    """Supported stdin payload formats."""

    JSON = "json"
    TOML = "toml"
    ADDRESSES = "addresses"


class Reliability(StrEnum):
    """Coarse provider reliability classification."""

    PUBLIC_BEST_EFFORT = "public-best-effort"
    PUBLIC_DOCUMENTED = "public-documented"
    KEYED_DOCUMENTED = "keyed-documented"
    PAID_PRODUCTION = "paid-production"


@dataclass(frozen=True)
class DerivedAddress:
    """A derived address plus its branch/index context."""

    branch: int
    index: int
    path_label: str
    address: str


@dataclass(frozen=True)
class ScanTarget:
    """One chain-specific public input to scan."""

    chain: ChainSymbol
    mode: InputMode
    value: str
    count: int | None = None
    branches: tuple[int, ...] = (0,)
    provider_order: tuple[str, ...] = ()
    label: str | None = None


@dataclass(frozen=True)
class ScanRequest:
    """Top-level request describing a full reporting run."""

    label: str
    max_count: int
    targets: tuple[ScanTarget, ...]
    output_dir: Path = Path("output")
    formats: tuple[OutputFormat, ...] = (OutputFormat.TXT, OutputFormat.JSON)


@dataclass(frozen=True)
class ReportRow:
    """One address report row."""

    index: int | str
    address: str
    tx_count: int
    balance_native: Decimal
    balance_usd: Decimal | None = None
    notes: tuple[str, ...] = ()
    provider_id: str | None = None

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
    providers_tried: tuple[str, ...] = ()


@dataclass(frozen=True)
class RunResult:
    """Result for a full project run."""

    output_dir: Path
    formats: tuple[OutputFormat, ...] = (OutputFormat.TXT, OutputFormat.JSON)
    chains: dict[ChainSymbol, ChainRunResult] = field(default_factory=dict)


@dataclass(frozen=True)
class ProviderMetadata:
    """Descriptive metadata for one address-activity backend."""

    provider_id: str
    display_name: str
    supported_chains: tuple[ChainSymbol, ...]
    requires_api_key: bool
    signup_required: bool
    free_tier: bool
    multichain: bool
    reliability: Reliability
    docs_url: str
    rate_limits: str
    notes: str
