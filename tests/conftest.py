from __future__ import annotations

from decimal import Decimal

import pytest

from address_generator.clients import (
    BlockscoutAddressProvider,
    BscScanAddressProvider,
    EsploraAddressProvider,
    EthplorerAddressProvider,
    PriceClient,
    ProviderCatalog,
    ProviderRouter,
    SoChainAddressProvider,
    ZcashInfoAddressProvider,
)
from address_generator.derivation import AddressDeriver, AddressInputLoader, ExtendedKeyNormalizer
from address_generator.models import ChainSymbol
from address_generator.services import PortfolioScanService


class FakeHttpClient:
    def __init__(
        self,
        responses: dict[
            tuple[str, tuple[tuple[str, str], ...] | None, tuple[tuple[str, str], ...] | None],
            object,
        ],
    ) -> None:
        self._responses = responses

    def get_json(
        self,
        url: str,
        params: dict[str, str] | None = None,
        *,
        headers: dict[str, str] | None = None,
    ) -> object:
        key = (
            url,
            tuple(sorted(params.items())) if params else None,
            tuple(sorted(headers.items())) if headers else None,
        )
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
                (("ids", "bitcoin-cash"), ("vs_currencies", "usd")),
                None,
            ): {"bitcoin-cash": {"usd": 450.0}},
            (
                "https://api.coingecko.com/api/v3/simple/price",
                (("ids", "bitcoin"), ("vs_currencies", "usd")),
                None,
            ): {"bitcoin": {"usd": 60000.0}},
            (
                "https://api.coingecko.com/api/v3/simple/price",
                (("ids", "ethereum"), ("vs_currencies", "usd")),
                None,
            ): {"ethereum": {"usd": 1500.0}},
            (
                "https://api.coingecko.com/api/v3/simple/price",
                (("ids", "dogecoin"), ("vs_currencies", "usd")),
                None,
            ): {"dogecoin": {"usd": 0.1}},
            (
                "https://api.coingecko.com/api/v3/simple/price",
                (("ids", "ethereum-classic"), ("vs_currencies", "usd")),
                None,
            ): {"ethereum-classic": {"usd": 25.0}},
            (
                "https://api.coingecko.com/api/v3/simple/price",
                (("ids", "matic-network"), ("vs_currencies", "usd")),
                None,
            ): {"matic-network": {"usd": 0.75}},
            (
                "https://api.coingecko.com/api/v3/simple/price",
                (("ids", "zcash"), ("vs_currencies", "usd")),
                None,
            ): {"zcash": {"usd": 30.0}},
            (
                "https://blockstream.info/api/address/bc1qexample",
                None,
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
                "https://bchexplorer.cash/api/address/1BCHexample",
                None,
                None,
            ): {
                "address": "bitcoincash:qexample",
                "chain_stats": {
                    "funded_txo_count": 2,
                    "funded_txo_sum": 500000000,
                    "spent_txo_count": 0,
                    "spent_txo_sum": 0,
                    "tx_count": 2,
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
                None,
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
            (
                "https://chain.so/api/v3/balance/DOGE/Dabc",
                None,
                (("API-KEY", "test-key"),),
            ): {
                "status": "success",
                "data": {"balance": {"total": "25.5"}},
            },
            (
                "https://chain.so/api/v3/transaction_counts/DOGE/Dabc",
                None,
                (("API-KEY", "test-key"),),
            ): {
                "status": "success",
                "data": {"transaction_counts": {"total": 4}},
            },
            (
                "https://api.zcashinfo.com/api/v1/addresses/t1abc",
                None,
                None,
            ): {
                "address": "t1abc",
                "address_type": "p2pkh",
                "network": "mainnet",
                "balance_zatoshis": 123000000,
                "balance_zec": "1.23000000",
                "received_zatoshis": 123000000,
                "received_zec": "1.23000000",
                "utxo_count": 1,
            },
            (
                "https://api.zcashinfo.com/api/v1/addresses/t1abc/txs",
                None,
                None,
            ): {
                "address": "t1abc",
                "total_count": 3,
                "start_height": 1,
                "end_height": 1,
                "transactions": [],
            },
            (
                "https://etc.blockscout.com/api/v2/addresses/0xetc",
                None,
                None,
            ): {
                "hash": "0xetc",
                "coin_balance": "2000000000000000000",
                "exchange_rate": "25.0",
            },
            (
                "https://etc.blockscout.com/api/v2/addresses/0xetc/counters",
                None,
                None,
            ): {
                "transactions_count": "7",
            },
            (
                "https://api.bscscan.com/api",
                (
                    ("action", "balance"),
                    ("address", "0xbsc"),
                    ("apikey", "bsc-key"),
                    ("module", "account"),
                    ("tag", "latest"),
                ),
                None,
            ): {
                "status": "1",
                "message": "OK",
                "result": "3000000000000000000",
            },
            (
                "https://api.bscscan.com/api",
                (
                    ("action", "txlist"),
                    ("address", "0xbsc"),
                    ("apikey", "bsc-key"),
                    ("endblock", "99999999"),
                    ("module", "account"),
                    ("offset", "10000"),
                    ("page", "1"),
                    ("sort", "asc"),
                    ("startblock", "0"),
                ),
                None,
            ): {
                "status": "1",
                "message": "OK",
                "result": [{}, {}],
            },
        }
    )


@pytest.fixture
def provider_catalog(fake_http_client: FakeHttpClient) -> ProviderCatalog:
    return ProviderCatalog(
        providers={
            "blockstream-public": EsploraAddressProvider(
                provider_id="blockstream-public",
                api_base="https://blockstream.info/api",
                supported_chains=(ChainSymbol.BTC,),
                http_client=fake_http_client,
            ),
            "bch-explorer-public": EsploraAddressProvider(
                provider_id="bch-explorer-public",
                api_base="https://bchexplorer.cash/api",
                supported_chains=(ChainSymbol.BCH,),
                http_client=fake_http_client,
            ),
            "ethplorer": EthplorerAddressProvider(http_client=fake_http_client),
            "sochain": SoChainAddressProvider(http_client=fake_http_client, api_key="test-key"),
            "zcashinfo-public": ZcashInfoAddressProvider(http_client=fake_http_client),
            "etc-blockscout": BlockscoutAddressProvider(
                provider_id="etc-blockscout",
                api_base="https://etc.blockscout.com/api/v2",
                supported_chains=(ChainSymbol.ETC,),
                http_client=fake_http_client,
            ),
            "bscscan": BscScanAddressProvider(http_client=fake_http_client, api_key="bsc-key"),
        }
    )


@pytest.fixture
def scan_service(
    address_deriver: AddressDeriver,
    address_loader: AddressInputLoader,
    fake_http_client: FakeHttpClient,
    provider_catalog: ProviderCatalog,
) -> PortfolioScanService:
    return PortfolioScanService(
        address_deriver=address_deriver,
        address_input_loader=address_loader,
        price_client=PriceClient(fake_http_client),
        provider_router=ProviderRouter(provider_catalog),
    )


@pytest.fixture
def one_btc() -> Decimal:
    return Decimal("1")
