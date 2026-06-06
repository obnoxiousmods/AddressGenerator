"""HTTP, pricing, provider routing, and explorer clients."""

from __future__ import annotations

import csv
import io
import json
import os
import time
from dataclasses import dataclass, field
from decimal import Decimal
from hashlib import sha1
from pathlib import Path
from typing import Any, Protocol, cast

import requests

from address_generator.api_types import (
    CoinGeckoPriceDict,
    EthAddressResponseDict,
    SoChainResponseDict,
    UtxoAddressResponseDict,
)
from address_generator.constants import (
    BTC,
    COINGECKO_URL,
    DEFAULT_PROVIDER_ORDER,
    ETHPLORER_URL,
    LTC,
    PROVIDER_METADATA,
    SATOSHI,
    SOCHAIN_URL,
    WEI,
)
from address_generator.exceptions import ExplorerApiError
from address_generator.models import ChainSymbol, ProviderMetadata, ReportRow

COIN_IDS = {
    ChainSymbol.BTC: BTC.coin_gecko_id,
    ChainSymbol.LTC: LTC.coin_gecko_id,
    ChainSymbol.DOGE: "dogecoin",
    ChainSymbol.ETH: "ethereum",
}


class SupportsGetJson(Protocol):
    """Protocol for HTTP clients that expose ``get_json``."""

    def get_json(
        self,
        url: str,
        params: dict[str, str] | None = None,
        *,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Fetch JSON from a URL."""


class SupportsPriceLookup(Protocol):
    """Protocol for components that can fetch USD prices."""

    def fetch_prices(self, chains: tuple[ChainSymbol, ...]) -> dict[ChainSymbol, Decimal]:
        """Return prices for a chain selection."""


class SupportsAddressActivityProvider(Protocol):
    """Protocol for address activity providers."""

    provider_id: str

    def supports_chain(self, chain: ChainSymbol) -> bool:
        """Return whether the provider supports a chain."""

    def scan_address(
        self,
        chain: ChainSymbol,
        index: int | str,
        address: str,
        usd_price: Decimal | None,
    ) -> ReportRow:
        """Scan one address."""


@dataclass
class JsonHttpClient:
    """JSON HTTP wrapper with optional filesystem caching."""

    session: requests.Session = field(default_factory=requests.Session)
    timeout_seconds: int = 30
    cache_dir: Path = Path(".cache/address_generator/http")
    cache_ttl_seconds: int = 300

    def get_json(
        self,
        url: str,
        params: dict[str, str] | None = None,
        *,
        headers: dict[str, str] | None = None,
    ) -> Any:
        """Fetch and decode JSON, using a short-lived file cache when possible."""

        cache_path = self._cache_path(url, params, headers)
        cached = self._read_cache(cache_path)
        if cached is not None:
            return cached

        response = self.session.get(
            url,
            params=params,
            timeout=self.timeout_seconds,
            headers={
                "User-Agent": "AddressGenerator/0.3",
                **(headers or {}),
            },
        )
        response.raise_for_status()
        payload = response.json()
        self._write_cache(cache_path, payload)
        return payload

    def _cache_path(
        self,
        url: str,
        params: dict[str, str] | None,
        headers: dict[str, str] | None,
    ) -> Path:
        fingerprint_input = (
            url,
            sorted((params or {}).items()),
            sorted((headers or {}).items()),
        )
        fingerprint = sha1(
            repr(fingerprint_input).encode("utf-8"),
            usedforsecurity=False,
        ).hexdigest()
        return self.cache_dir / f"{fingerprint}.json"

    def _read_cache(self, path: Path) -> Any | None:
        if not path.exists():
            return None
        age_seconds = time.time() - path.stat().st_mtime
        if age_seconds > self.cache_ttl_seconds:
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def _write_cache(self, path: Path, payload: Any) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload), encoding="utf-8")


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
        return self._parse_prices(cast(dict[str, CoinGeckoPriceDict], payload))

    def _parse_prices(self, payload: dict[str, CoinGeckoPriceDict]) -> dict[ChainSymbol, Decimal]:
        prices: dict[ChainSymbol, Decimal] = {}
        for chain, coin_id in COIN_IDS.items():
            if coin_id is None:
                continue
            entry = payload.get(coin_id)
            if entry and "usd" in entry:
                prices[chain] = Decimal(str(entry["usd"]))
        return prices


@dataclass
class EsploraAddressProvider:
    """Esplora-style provider for BTC/LTC public explorers."""

    provider_id: str
    api_base: str
    supported_chains: tuple[ChainSymbol, ...]
    http_client: SupportsGetJson

    def supports_chain(self, chain: ChainSymbol) -> bool:
        return chain in self.supported_chains

    def scan_address(
        self,
        chain: ChainSymbol,
        index: int | str,
        address: str,
        usd_price: Decimal | None,
    ) -> ReportRow:
        payload = self.http_client.get_json(f"{self.api_base}/address/{address}")
        if not isinstance(payload, dict) or "chain_stats" not in payload:
            msg = f"Unexpected {self.provider_id} response for {chain}:{address}"
            raise ExplorerApiError(msg)

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
            provider_id=self.provider_id,
        )


@dataclass
class SoChainAddressProvider:
    """SoChain-backed provider for BTC, LTC, and DOGE."""

    http_client: SupportsGetJson
    api_key: str | None = None
    provider_id: str = "sochain"

    def supports_chain(self, chain: ChainSymbol) -> bool:
        return chain in {ChainSymbol.BTC, ChainSymbol.LTC, ChainSymbol.DOGE}

    def scan_address(
        self,
        chain: ChainSymbol,
        index: int | str,
        address: str,
        usd_price: Decimal | None,
    ) -> ReportRow:
        api_key = self.api_key or os.getenv("SOCHAIN_API_KEY")
        if not api_key:
            raise ExplorerApiError(
                "SoChain requires SOCHAIN_API_KEY for keyed requests. "
                "Create one at https://chain.so/api."
            )

        network = chain.value
        headers = {"API-KEY": api_key}
        balance_payload = cast(
            SoChainResponseDict,
            self.http_client.get_json(
                f"{SOCHAIN_URL}/balance/{network}/{address}",
                headers=headers,
            ),
        )
        tx_count_payload = cast(
            SoChainResponseDict,
            self.http_client.get_json(
                f"{SOCHAIN_URL}/transaction_counts/{network}/{address}",
                headers=headers,
            ),
        )
        if (
            balance_payload.get("status") != "success"
            or tx_count_payload.get("status") != "success"
        ):
            raise ExplorerApiError(f"SoChain returned a non-success status for {chain}:{address}")

        balance_total = Decimal(
            str(balance_payload.get("data", {}).get("balance", {}).get("total", "0"))
        )
        tx_count = int(
            tx_count_payload.get("data", {}).get("transaction_counts", {}).get("total", 0)
        )
        balance_usd = balance_total * usd_price if usd_price is not None else None
        return ReportRow(
            index=index,
            address=address,
            tx_count=tx_count,
            balance_native=balance_total,
            balance_usd=balance_usd,
            provider_id=self.provider_id,
        )


@dataclass
class EthplorerAddressProvider:
    """Ethplorer-backed provider for ETH and ERC-20 holdings."""

    http_client: SupportsGetJson
    api_key: str = "freekey"
    provider_id: str = "ethplorer"

    def supports_chain(self, chain: ChainSymbol) -> bool:
        return chain is ChainSymbol.ETH

    def scan_address(
        self,
        chain: ChainSymbol,
        index: int | str,
        address: str,
        usd_price: Decimal | None,
    ) -> ReportRow:
        del chain, usd_price
        payload = self.http_client.get_json(
            ETHPLORER_URL.format(address=address),
            params={"apiKey": self.api_key, "showTxsCount": "true"},
        )
        if not isinstance(payload, dict):
            raise ExplorerApiError(f"Unexpected Ethplorer response for ETH:{address}")
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
            provider_id=self.provider_id,
        )

    def _format_token_notes(self, response: EthAddressResponseDict) -> list[str]:
        rendered: list[str] = []
        for token in response.get("tokens", [])[:25]:
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


@dataclass
class ProviderCatalog:
    """Catalog of available providers and their metadata."""

    providers: dict[str, SupportsAddressActivityProvider]
    metadata: dict[str, ProviderMetadata] = field(default_factory=lambda: dict(PROVIDER_METADATA))

    def list_metadata(self) -> list[ProviderMetadata]:
        """Return provider metadata in stable order."""

        return [self.metadata[key] for key in sorted(self.metadata)]

    def resolve_order(
        self,
        chain: ChainSymbol,
        provider_order: tuple[str, ...] | None = None,
    ) -> list[SupportsAddressActivityProvider]:
        """Resolve the ordered providers to try for a chain."""

        selected_order = provider_order or DEFAULT_PROVIDER_ORDER[chain]
        resolved: list[SupportsAddressActivityProvider] = []
        for provider_id in selected_order:
            provider = self.providers.get(provider_id)
            if provider is not None and provider.supports_chain(chain):
                resolved.append(provider)
        if not resolved:
            raise ExplorerApiError(f"No providers configured for chain {chain.value}")
        return resolved

    def describe_as_csv(self) -> str:
        """Serialize provider metadata as CSV."""

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "provider_id",
                "display_name",
                "supported_chains",
                "requires_api_key",
                "signup_required",
                "free_tier",
                "multichain",
                "reliability",
                "rate_limits",
                "docs_url",
                "notes",
            ]
        )
        for item in self.list_metadata():
            writer.writerow(
                [
                    item.provider_id,
                    item.display_name,
                    ",".join(chain.value for chain in item.supported_chains),
                    item.requires_api_key,
                    item.signup_required,
                    item.free_tier,
                    item.multichain,
                    item.reliability.value,
                    item.rate_limits,
                    item.docs_url,
                    item.notes,
                ]
            )
        return output.getvalue()


@dataclass
class ProviderRouter:
    """Try providers in order until one returns a report row."""

    catalog: ProviderCatalog

    def scan_address(
        self,
        chain: ChainSymbol,
        index: int | str,
        address: str,
        usd_price: Decimal | None,
        provider_order: tuple[str, ...] | None = None,
    ) -> tuple[ReportRow, tuple[str, ...]]:
        """Scan an address using the first working provider."""

        providers = self.catalog.resolve_order(chain, provider_order)
        tried: list[str] = []
        last_error: ExplorerApiError | None = None
        for provider in providers:
            tried.append(provider.provider_id)
            try:
                return provider.scan_address(chain, index, address, usd_price), tuple(tried)
            except ExplorerApiError as exc:
                last_error = exc
                continue
        if last_error is None:
            raise ExplorerApiError(f"No providers available for {chain.value}")
        raise last_error
