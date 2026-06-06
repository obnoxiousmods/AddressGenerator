from __future__ import annotations

from decimal import Decimal

from address_generator.clients import SupportsEthereumScan, SupportsPriceLookup, SupportsUtxoScan
from address_generator.derivation import AddressDeriver, AddressInputLoader, ExtendedKeyNormalizer
from address_generator.models import ChainSymbol, InputMode, ReportRow, ScanTarget
from address_generator.services import PortfolioScanService


def test_scan_service_builds_utxo_rows(scan_service: PortfolioScanService) -> None:
    target = ScanTarget(chain=ChainSymbol.BTC, mode=InputMode.ADDRESSES, value="bc1qexample")
    rows = scan_service.build_rows(target, 1)
    assert len(rows) == 1
    assert rows[0].balance_native == Decimal("1")


def test_scan_service_builds_eth_rows(scan_service: PortfolioScanService) -> None:
    target = ScanTarget(chain=ChainSymbol.ETH, mode=InputMode.ADDRESSES, value="0xabc")
    rows = scan_service.build_rows(target, 1)
    assert len(rows) == 1
    assert rows[0].notes == ("USDT=2.5 ($2.50)",)


def test_scan_service_summarizes_rows(scan_service: PortfolioScanService) -> None:
    target = ScanTarget(chain=ChainSymbol.BTC, mode=InputMode.ADDRESSES, value="bc1qexample")
    rows = scan_service.build_rows(target, 1)
    summary = scan_service.summarize_rows(rows)
    assert summary.total_native_balance == Decimal("1")
    assert summary.active_count == 1


def test_scan_service_builds_xpub_addresses() -> None:
    class NoPriceClient(SupportsPriceLookup):
        def fetch_prices(self, chains: tuple[ChainSymbol, ...]) -> dict[ChainSymbol, Decimal]:
            return {}

    class NoopUtxo(SupportsUtxoScan):
        def scan_address(
            self,
            chain: ChainSymbol,
            index: int,
            address: str,
            usd_price: Decimal | None,
        ) -> ReportRow:
            return ReportRow(index=index, address=address, tx_count=0, balance_native=Decimal("0"))

    class NoopEth(SupportsEthereumScan):
        def scan_address(self, index: int, address: str) -> ReportRow:
            return ReportRow(index=index, address=address, tx_count=0, balance_native=Decimal("0"))

    service = PortfolioScanService(
        address_deriver=AddressDeriver(ExtendedKeyNormalizer()),
        address_input_loader=AddressInputLoader(),
        price_client=NoPriceClient(),
        utxo_explorer_client=NoopUtxo(),
        ethereum_explorer_client=NoopEth(),
    )
    target = ScanTarget(
        chain=ChainSymbol.BTC,
        mode=InputMode.XPUB,
        value=(
            "zpub6rFR7y4Q2AijBEqTUquhVz398htDFrtymD9xYYfG1m4wAcvPhXNfE3EfH1r1"
            "ADqtfSdVCToUG868RvUUkgDKf31mGDtKsAYz2oz2AGutZYs"
        ),
    )
    rows = service.build_rows(target, 1)
    assert rows[0].address == "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu"
