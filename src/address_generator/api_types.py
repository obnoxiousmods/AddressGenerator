"""Typed views of third-party API responses used by the project."""

from __future__ import annotations

from typing import NotRequired, TypedDict


class UtxoStatsDict(TypedDict):
    """Transaction and value aggregates returned by an Esplora-style API."""

    funded_txo_count: int
    funded_txo_sum: int
    spent_txo_count: int
    spent_txo_sum: int
    tx_count: int


class UtxoAddressResponseDict(TypedDict):
    """Address payload returned by BTC, LTC, and DOGE explorers."""

    address: str
    chain_stats: UtxoStatsDict
    mempool_stats: UtxoStatsDict


class CoinGeckoPriceDict(TypedDict):
    """USD-only CoinGecko price snapshot."""

    usd: float


class EthAssetPriceDict(TypedDict, total=False):
    """Optional token or ETH price payload."""

    rate: float


class EthAssetInfoDict(TypedDict, total=False):
    """Metadata for an ERC-20 or ETH-like asset."""

    symbol: str
    name: str
    decimals: str
    price: EthAssetPriceDict


class EthTokenBalanceDict(TypedDict):
    """Raw Ethplorer token-balance record."""

    balance: str
    tokenInfo: EthAssetInfoDict


class EthAddressBalanceDict(TypedDict, total=False):
    """ETH-native balance section."""

    balance: float
    rawBalance: str
    price: EthAssetPriceDict


class EthAddressResponseDict(TypedDict):
    """Address-level Ethplorer response."""

    address: str
    countTxs: NotRequired[int]
    ETH: NotRequired[EthAddressBalanceDict]
    tokens: NotRequired[list[EthTokenBalanceDict]]


class SoChainAmountDict(TypedDict, total=False):
    """Balance payload fields returned by SoChain."""

    confirmed: str
    unconfirmed: str
    total: str


class SoChainTransactionCountsDict(TypedDict, total=False):
    """Transaction count fields returned by SoChain."""

    total: int
    confirmed: int
    unconfirmed: int


class SoChainResponseDataDict(TypedDict, total=False):
    """Generic SoChain v3 response payload."""

    balance: SoChainAmountDict
    transaction_counts: SoChainTransactionCountsDict


class SoChainResponseDict(TypedDict):
    """Top-level SoChain v3 response."""

    status: str
    data: SoChainResponseDataDict
