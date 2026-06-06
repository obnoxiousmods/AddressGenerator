from __future__ import annotations

from decimal import Decimal

from conftest import FakeHttpClient

from address_generator.clients import EthereumExplorerClient, PriceClient, UtxoExplorerClient
from address_generator.models import ChainSymbol


def test_price_client_parses_known_prices(fake_http_client: FakeHttpClient) -> None:
    client = PriceClient(fake_http_client)
    prices = client.fetch_prices((ChainSymbol.BTC,))
    assert prices[ChainSymbol.BTC] == Decimal("60000.0")


def test_utxo_explorer_client_builds_report_row(fake_http_client: FakeHttpClient) -> None:
    client = UtxoExplorerClient(fake_http_client)
    row = client.scan_address(ChainSymbol.BTC, 0, "bc1qexample", Decimal("60000"))
    assert row.tx_count == 1
    assert row.balance_native == Decimal("1")
    assert row.balance_usd == Decimal("60000")


def test_eth_explorer_client_formats_token_notes(fake_http_client: FakeHttpClient) -> None:
    client = EthereumExplorerClient(fake_http_client)
    row = client.scan_address(0, "0xabc")
    assert row.tx_count == 3
    assert row.balance_native == Decimal("2")
    assert row.balance_usd == Decimal("3000.0")
    assert row.notes == ("USDT=2.5 ($2.50)",)
