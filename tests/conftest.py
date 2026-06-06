from __future__ import annotations

from decimal import Decimal

import pytest

from address_generator.clients import EthereumExplorerClient, PriceClient, UtxoExplorerClient
from address_generator.derivation import AddressDeriver, AddressInputLoader, ExtendedKeyNormalizer
from address_generator.services import PortfolioScanService


class FakeHttpClient:
    def __init__(
        self,
        responses: dict[tuple[str, tuple[tuple[str, str], ...] | None], object],
    ) -> None:
        self._responses = responses

    def get_json(self, url: str, params: dict[str, str] | None = None) -> object:
        key = (url, tuple(sorted(params.items())) if params else None)
        return self._responses[key]


@pytest.fixture
def normalizer() -> ExtendedKeyNormalizer:
    return ExtendedKeyNormalizer()


@pytest.fixture
def address_deriver(normalizer: ExtendedKeyNormalizer) -> AddressDeriver:
    return AddressDeriver(normalizer=normalizer)


@pytest.fixture
def address_loader() -> AddressInputLoader:
    return AddressInputLoader()


@pytest.fixture
def fake_http_client() -> FakeHttpClient:
    return FakeHttpClient(
        {
            (
                "https://api.coingecko.com/api/v3/simple/price",
                (("ids", "bitcoin"), ("vs_currencies", "usd")),
            ): {"bitcoin": {"usd": 60000.0}},
            (
                "https://api.coingecko.com/api/v3/simple/price",
                (("ids", "ethereum"), ("vs_currencies", "usd")),
            ): {"ethereum": {"usd": 1500.0}},
            (
                "https://blockstream.info/api/address/bc1qexample",
                None,
            ): {
                "address": "bc1qexample",
                "chain_stats": {
                    "funded_txo_count": 1,
                    "funded_txo_sum": 100000000,
                    "spent_txo_count": 0,
                    "spent_txo_sum": 0,
                    "tx_count": 1,
                },
                "mempool_stats": {
                    "funded_txo_count": 0,
                    "funded_txo_sum": 0,
                    "spent_txo_count": 0,
                    "spent_txo_sum": 0,
                    "tx_count": 0,
                },
            },
            (
                "https://api.ethplorer.io/getAddressInfo/0xabc",
                (("apiKey", "freekey"), ("showTxsCount", "true")),
            ): {
                "address": "0xabc",
                "countTxs": 3,
                "ETH": {
                    "rawBalance": "2000000000000000000",
                    "price": {"rate": 1500.0},
                },
                "tokens": [
                    {
                        "balance": "2500000",
                        "tokenInfo": {
                            "symbol": "USDT",
                            "decimals": "6",
                            "price": {"rate": 1.0},
                        },
                    }
                ],
            },
        }
    )


@pytest.fixture
def scan_service(
    address_deriver: AddressDeriver,
    address_loader: AddressInputLoader,
    fake_http_client: FakeHttpClient,
) -> PortfolioScanService:
    return PortfolioScanService(
        address_deriver=address_deriver,
        address_input_loader=address_loader,
        price_client=PriceClient(fake_http_client),  # type: ignore[arg-type]
        utxo_explorer_client=UtxoExplorerClient(fake_http_client),  # type: ignore[arg-type]
        ethereum_explorer_client=EthereumExplorerClient(fake_http_client),  # type: ignore[arg-type]
    )


@pytest.fixture
def one_btc() -> Decimal:
    return Decimal("1")
