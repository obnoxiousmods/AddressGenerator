"""HTTP, pricing, and explorer clients."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Protocol, cast

import requests

from address_generator.api_types import (
    CoinGeckoPriceDict,
    EthAddressResponseDict,
    UtxoAddressResponseDict,
)
from address_generator.constants import BTC, COINGECKO_URL, DOGE, ETHPLORER_URL, LTC, SATOSHI, WEI
from address_generator.exceptions import ExplorerApiError
from address_generator.models import ChainSymbol, ReportRow

COIN_IDS = {
    ChainSymbol.BTC: BTC.coin_gecko_id,
    ChainSymbol.LTC: LTC.coin_gecko_id,
    ChainSymbol.DOGE: DOGE.coin_gecko_id,
    ChainSymbol.ETH: "ethereum",
}

CHAIN_APIS = {
    ChainSymbol.BTC: BTC.api_base,
    ChainSymbol.LTC: LTC.api_base,
    ChainSymbol.DOGE: DOGE.api_base,
}


class SupportsGetJson(Protocol):
    """Protocol for HTTP clients that expose ``get_json``."""

    def get_json(self, url: str, params: dict[str, str] | None = None) -> Any:
        """Fetch JSON from a URL."""


@dataclass
class JsonHttpClient:
    """Small JSON HTTP wrapper with a consistent user agent."""

    session: requests.Session = field(default_factory=requests.Session)
    timeout_seconds: int = 30

    def get_json(self, url: str, params: dict[str, str] | None = None) -> Any:
        """Fetch and decode JSON."""

        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout_seconds,
            headers={"User-Agent": "AddressGenerator/0.2"},
        )
        response.raise_for_status()
        return response.json()


class SupportsPriceLookup(Protocol):
    """Protocol for components that can fetch USD prices."""

    def fetch_prices(self, chains: tuple[ChainSymbol, ...]) -> dict[ChainSymbol, Decimal]:
        """Return prices for a chain selection."""


class SupportsUtxoScan(Protocol):
    """Protocol for UTXO explorer lookups."""

    def scan_address(
        self,
        chain: ChainSymbol,
        index: int,
        address: str,
        usd_price: Decimal | None,
    ) -> ReportRow:
        """Return one UTXO report row."""


class SupportsEthereumScan(Protocol):
    """Protocol for Ethereum explorer lookups."""

    def scan_address(self, index: int, address: str) -> ReportRow:
        """Return one Ethereum report row."""


@dataclass
class PriceClient:
    """Fetch spot prices for supported chains."""

    http_client: SupportsGetJson

    def fetch_prices(self, chains: tuple[ChainSymbol, ...]) -> dict[ChainSymbol, Decimal]:
        """Return USD prices for requested chain symbols."""

        coin_ids = [coin_id for chain in chains if (coin_id := COIN_IDS.get(chain)) is not None]
        if not coin_ids:
            return {}

        payload = self.http_client.get_json(
            COINGECKO_URL,
            params={"ids": ",".join(coin_ids), "vs_currencies": "usd"},
        )
        return self._parse_prices(payload)

    def _parse_prices(self, payload: dict[str, CoinGeckoPriceDict]) -> dict[ChainSymbol, Decimal]:
        """Convert a CoinGecko response into chain-keyed decimals."""

        prices: dict[ChainSymbol, Decimal] = {}
        for chain, coin_id in COIN_IDS.items():
            if coin_id is None:
                continue
            entry = payload.get(coin_id)
            if entry and "usd" in entry:
                prices[chain] = Decimal(str(entry["usd"]))
        return prices


@dataclass
class UtxoExplorerClient:
    """Scan UTXO-style addresses via Esplora-compatible APIs."""

    http_client: SupportsGetJson

    def scan_address(
        self,
        chain: ChainSymbol,
        index: int,
        address: str,
        usd_price: Decimal | None,
    ) -> ReportRow:
        """Fetch tx count and balance for one UTXO address."""

        api_base = CHAIN_APIS[chain]
        payload = self.http_client.get_json(f"{api_base}/address/{address}")
        if not isinstance(payload, dict) or "chain_stats" not in payload:
            raise ExplorerApiError(f"Unexpected {chain} explorer response for address {address}")

        response = cast(UtxoAddressResponseDict, payload)
        stats = response["chain_stats"]
        funded = Decimal(stats["funded_txo_sum"])
        spent = Decimal(stats["spent_txo_sum"])
        balance = (funded - spent) / SATOSHI
        balance_usd = balance * usd_price if usd_price is not None else None
        return ReportRow(
            index=index,
            address=address,
            tx_count=stats["tx_count"],
            balance_native=balance,
            balance_usd=balance_usd,
        )


@dataclass
class EthereumExplorerClient:
    """Scan ETH addresses and format token holdings."""

    http_client: SupportsGetJson

    def scan_address(self, index: int, address: str) -> ReportRow:
        """Fetch ETH balance, tx count, and token holdings for an address."""

        payload = self.http_client.get_json(
            ETHPLORER_URL.format(address=address),
            params={"apiKey": "freekey", "showTxsCount": "true"},
        )
        if not isinstance(payload, dict):
            raise ExplorerApiError(f"Unexpected ETH explorer response for address {address}")
        response = cast(EthAddressResponseDict, payload)

        eth_section = response.get("ETH", {})
        raw_balance = Decimal(str(eth_section.get("rawBalance", "0")))
        eth_balance = raw_balance / WEI
        usd_rate = eth_section.get("price", {}).get("rate")
        balance_usd = eth_balance * Decimal(str(usd_rate)) if usd_rate is not None else None
        notes = tuple(self._format_token_notes(response))

        return ReportRow(
            index=index,
            address=address,
            tx_count=int(response.get("countTxs", 0)),
            balance_native=eth_balance,
            balance_usd=balance_usd,
            notes=notes,
        )

    def _format_token_notes(self, response: EthAddressResponseDict) -> list[str]:
        """Render token balances into compact notes."""

        rendered: list[str] = []
        for token in response.get("tokens", [])[:15]:
            info = token.get("tokenInfo", {})
            symbol = info.get("symbol") or info.get("name") or "TOKEN"
            decimals = int(info.get("decimals") or "0")
            balance = Decimal(str(token.get("balance", "0")))
            normalized = balance / (Decimal(10) ** decimals if decimals else Decimal(1))
            if normalized <= 0:
                continue
            note = f"{symbol}={normalized.normalize()}"
            rate = info.get("price", {}).get("rate")
            if rate is not None:
                usd = normalized * Decimal(str(rate))
                note = f"{note} (${usd.quantize(Decimal('0.01'))})"
            rendered.append(note)
        return rendered
