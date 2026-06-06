from __future__ import annotations

from decimal import Decimal

from conftest import FakeHttpClient

from address_generator.clients import (
    EsploraAddressProvider,
    EthplorerAddressProvider,
    PriceClient,
    SoChainAddressProvider,
)
from address_generator.models import ChainSymbol


def test_price_client_parses_known_prices(fake_http_client: FakeHttpClient) -> None:
    client = PriceClient(fake_http_client)
    prices = client.fetch_prices((ChainSymbol.BTC,))
    assert prices[ChainSymbol.BTC] == Decimal("60000.0")


def test_utxo_explorer_client_builds_report_row(fake_http_client: FakeHttpClient) -> None:
    client = EsploraAddressProvider(
        provider_id="blockstream-public",
        api_base="https://blockstream.info/api",
        supported_chains=(ChainSymbol.BTC,),
        http_client=fake_http_client,
    )
    row = client.scan_address(ChainSymbol.BTC, "0/0", "bc1qexample", Decimal("60000"))
    assert row.tx_count == 1
    assert row.balance_native == Decimal("1")
    assert row.balance_usd == Decimal("60000")


def test_eth_explorer_client_formats_token_notes(fake_http_client: FakeHttpClient) -> None:
    client = EthplorerAddressProvider(http_client=fake_http_client)
    row = client.scan_address(ChainSymbol.ETH, "0/0", "0xabc", None)
    assert row.tx_count == 3
    assert row.balance_native == Decimal("2")
    assert row.balance_usd == Decimal("3000.0")
    assert row.notes == ("USDT=2.5 ($2.50)",)


def test_sochain_provider_builds_doge_row(fake_http_client: FakeHttpClient) -> None:
    client = SoChainAddressProvider(http_client=fake_http_client, api_key="test-key")
    row = client.scan_address(ChainSymbol.DOGE, "0/0", "Dabc", Decimal("0.1"))
    assert row.tx_count == 4
    assert row.balance_native == Decimal("25.5")
