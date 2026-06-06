"""Reusable orchestration services."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from address_generator.clients import (
    SupportsEthereumScan,
    SupportsPriceLookup,
    SupportsUtxoScan,
)
from address_generator.derivation import (
    AddressDeriver,
    AddressInputLoader,
    ensure_positive_count,
)
from address_generator.models import (
    ChainSymbol,
    InputMode,
    ReportRow,
    ScanSummary,
    ScanTarget,
)


@dataclass
class PortfolioScanService:
    """Coordinate derivation, explorer scanning, and summary generation."""

    address_deriver: AddressDeriver
    address_input_loader: AddressInputLoader
    price_client: SupportsPriceLookup
    utxo_explorer_client: SupportsUtxoScan
    ethereum_explorer_client: SupportsEthereumScan

    def build_rows(self, target: ScanTarget, max_count: int) -> tuple[ReportRow, ...]:
        """Build report rows for one target."""

        ensure_positive_count(max_count)
        prices = self.price_client.fetch_prices((target.chain,))
        addresses = self._resolve_addresses(target, max_count)

        if target.chain is ChainSymbol.ETH:
            return tuple(
                self.ethereum_explorer_client.scan_address(index, address)
                for index, address in enumerate(addresses)
            )

        price = prices.get(target.chain)
        return tuple(
            self.utxo_explorer_client.scan_address(target.chain, index, address, price)
            for index, address in enumerate(addresses)
        )

    def summarize_rows(self, rows: tuple[ReportRow, ...]) -> ScanSummary:
        """Build an aggregate summary from report rows."""

        return ScanSummary(
            total_count=len(rows),
            active_count=sum(1 for row in rows if row.is_active),
            total_native_balance=sum((row.balance_native for row in rows), Decimal("0")),
            total_usd_value=sum((row.balance_usd or Decimal("0") for row in rows), Decimal("0")),
        )

    def _resolve_addresses(self, target: ScanTarget, max_count: int) -> list[str]:
        """Load or derive addresses based on target mode."""

        if target.mode is InputMode.XPUB:
            return self.address_deriver.derive(target.chain, target.value, max_count)
        return self.address_input_loader.load(target.value, max_count)
