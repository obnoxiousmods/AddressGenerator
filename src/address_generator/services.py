"""Reusable orchestration services."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from decimal import Decimal

from address_generator.clients import (
    ProviderRouter,
    SupportsPriceLookup,
)
from address_generator.derivation import (
    AddressDeriver,
    AddressInputLoader,
    ensure_positive_count,
)
from address_generator.models import (
    ChainSymbol,
    DerivedAddress,
    InputMode,
    ReportRow,
    ScanSummary,
    ScanTarget,
)

ProgressCallback = Callable[[ChainSymbol, int, int, ReportRow | None], None]


@dataclass
class PortfolioScanService:
    """Coordinate derivation, explorer scanning, and summary generation."""

    address_deriver: AddressDeriver
    address_input_loader: AddressInputLoader
    price_client: SupportsPriceLookup
    provider_router: ProviderRouter

    def build_rows(
        self,
        target: ScanTarget,
        max_count: int,
        *,
        progress: ProgressCallback | None = None,
    ) -> tuple[ReportRow, ...]:
        """Build report rows for one target."""

        ensure_positive_count(max_count)
        effective_count = target.count or max_count
        prices = self.price_client.fetch_prices((target.chain,))
        addresses = self._resolve_addresses(target, effective_count)
        price = prices.get(target.chain)
        rows: list[ReportRow] = []
        total = len(addresses)
        for completed, derived in enumerate(addresses, start=1):
            row, providers_tried = self.provider_router.scan_address(
                target.chain,
                derived.path_label,
                derived.address,
                price,
                target.provider_order or None,
            )
            del providers_tried
            rows.append(row)
            if progress is not None:
                progress(target.chain, completed, total, row)
        return tuple(rows)

    def summarize_rows(self, rows: tuple[ReportRow, ...]) -> ScanSummary:
        """Build an aggregate summary from report rows."""

        return ScanSummary(
            total_count=len(rows),
            active_count=sum(1 for row in rows if row.is_active),
            total_native_balance=sum((row.balance_native for row in rows), Decimal("0")),
            total_usd_value=sum((row.balance_usd or Decimal("0") for row in rows), Decimal("0")),
        )

    def _resolve_addresses(self, target: ScanTarget, max_count: int) -> list[DerivedAddress]:
        """Load or derive addresses based on target mode."""

        if target.mode is InputMode.XPUB:
            return self.address_deriver.derive_entries(
                target.chain,
                target.value,
                target.branches,
                max_count,
            )

        addresses = self.address_input_loader.load(target.value, max_count)
        return [
            DerivedAddress(branch=0, index=index, path_label=str(index), address=address)
            for index, address in enumerate(addresses)
        ]
