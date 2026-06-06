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


class BlockscoutAddressResponseDict(TypedDict, total=False):
    """Address payload returned by Blockscout v2."""

    hash: str
    coin_balance: str
    exchange_rate: str
    has_token_transfers: bool
    has_tokens: bool


class BlockscoutCountersResponseDict(TypedDict, total=False):
    """Counter payload returned by Blockscout v2."""

    transactions_count: str
    token_transfers_count: str
    validations_count: str
    logs_count: str
    token_balances_count: str


class ZcashInfoAddressResponseDict(TypedDict):
    """Transparent-address payload returned by zcashinfo."""

    address: str
    address_type: str
    network: str
    balance_zatoshis: int
    balance_zec: str
    received_zatoshis: int
    received_zec: str
    utxo_count: int


class ZcashInfoTransactionsResponseDict(TypedDict):
    """Transactions payload returned by zcashinfo."""

    address: str
    total_count: int
    start_height: int
    end_height: int
    transactions: list[dict[str, object]]


class EtherscanStatusResponseDict(TypedDict):
    """Minimal Etherscan/BscScan status envelope."""

    status: str
    message: str
    result: str | list[dict[str, object]]
