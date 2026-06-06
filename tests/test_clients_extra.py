from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from typing import Any, cast

import pytest
import requests
from conftest import FakeHttpClient

from address_generator.clients import (
    JsonHttpClient,
    PriceClient,
    ProviderCatalog,
    ProviderRouter,
    SupportsAddressActivityProvider,
)
from address_generator.exceptions import ExplorerApiError
from address_generator.models import ChainSymbol, ReportRow


class FakeResponse:
    def __init__(self, payload: object, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            response = requests.Response()
            response.status_code = self.status_code
            raise requests.HTTPError(response=response)

    def json(self) -> object:
        return self.payload


class FakeSession:
    def __init__(self, payload: object, status_code: int = 200) -> None:
        self.payload = payload
        self.status_code = status_code
        self.calls = 0

    def get(
        self,
        url: str,
        params: dict[str, str] | None = None,
        timeout: int = 0,
        headers: dict[str, str] | None = None,
    ) -> FakeResponse:
        del url, params, timeout, headers
        self.calls += 1
        return FakeResponse(self.payload, status_code=self.status_code)


class FlakySession:
    def __init__(self) -> None:
        self.calls = 0

    def get(
        self,
        url: str,
        params: dict[str, str] | None = None,
        timeout: int = 0,
        headers: dict[str, str] | None = None,
    ) -> FakeResponse:
        del url, params, timeout, headers
        self.calls += 1
        if self.calls == 1:
            return FakeResponse({"error": "rate limit"}, status_code=429)
        return FakeResponse({"ok": True})


def test_json_http_client_uses_cache(tmp_path: Path) -> None:
    session = FakeSession({"ok": True})
    client = JsonHttpClient(session=cast(Any, session), cache_dir=tmp_path, cache_ttl_seconds=60)
    first = client.get_json("https://example.com/data", params={"a": "1"})
    second = client.get_json("https://example.com/data", params={"a": "1"})
    assert first == {"ok": True}
    assert second == {"ok": True}
    assert session.calls == 1


def test_json_http_client_retries_rate_limit(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sleeps: list[float] = []

    def fake_sleep(seconds: float) -> None:
        sleeps.append(seconds)

    monkeypatch.setattr("address_generator.clients.time.sleep", fake_sleep)
    session = FlakySession()
    client = JsonHttpClient(
        session=cast(Any, session),
        cache_dir=tmp_path,
        cache_ttl_seconds=0,
        retry_attempts=2,
        retry_backoff_seconds=0.25,
    )
    payload = client.get_json("https://example.com/data")
    assert payload == {"ok": True}
    assert session.calls == 2
    assert sleeps == [0.25]


def test_price_client_returns_empty_for_unknown_input(fake_http_client: FakeHttpClient) -> None:
    client = PriceClient(fake_http_client)
    assert client.fetch_prices(()) == {}


def test_provider_catalog_resolves_explicit_order(provider_catalog: ProviderCatalog) -> None:
    resolved = provider_catalog.resolve_order(
        ChainSymbol.BTC,
        provider_order=("sochain", "blockstream-public"),
    )
    assert [item.provider_id for item in resolved] == ["sochain", "blockstream-public"]


def test_provider_catalog_describes_csv(provider_catalog: ProviderCatalog) -> None:
    output = provider_catalog.describe_as_csv()
    assert "provider_id" in output
    assert "blockstream-public" in output


def test_provider_router_falls_back_after_error() -> None:
    class FailingProvider:
        provider_id = "fail"

        def supports_chain(self, chain: ChainSymbol) -> bool:
            del chain
            return True

        def scan_address(
            self,
            chain: ChainSymbol,
            index: int | str,
            address: str,
            usd_price: Decimal | None,
        ) -> ReportRow:
            del chain, index, address, usd_price
            raise ExplorerApiError("broken")

    class WorkingProvider:
        provider_id = "ok"

        def supports_chain(self, chain: ChainSymbol) -> bool:
            del chain
            return True

        def scan_address(
            self,
            chain: ChainSymbol,
            index: int | str,
            address: str,
            usd_price: Decimal | None,
        ) -> ReportRow:
            del chain, usd_price
            return ReportRow(index=index, address=address, tx_count=1, balance_native=Decimal("1"))

    catalog = ProviderCatalog(
        providers=cast(
            dict[str, SupportsAddressActivityProvider],
            {"fail": FailingProvider(), "ok": WorkingProvider()},
        ),
        metadata={},
    )
    row, tried = ProviderRouter(catalog).scan_address(
        ChainSymbol.BTC,
        "0/0",
        "bc1qexample",
        Decimal("1"),
        ("fail", "ok"),
    )
    assert row.address == "bc1qexample"
    assert tried == ("fail", "ok")


def test_provider_router_raises_last_error() -> None:
    class FailingProvider:
        provider_id = "fail"

        def supports_chain(self, chain: ChainSymbol) -> bool:
            del chain
            return True

        def scan_address(
            self,
            chain: ChainSymbol,
            index: int | str,
            address: str,
            usd_price: Decimal | None,
        ) -> ReportRow:
            del chain, index, address, usd_price
            raise ExplorerApiError("boom")

    catalog = ProviderCatalog(
        providers=cast(dict[str, SupportsAddressActivityProvider], {"fail": FailingProvider()}),
        metadata={},
    )
    with pytest.raises(ExplorerApiError, match="boom"):
        ProviderRouter(catalog).scan_address(
            ChainSymbol.BTC,
            "0/0",
            "bc1qexample",
            None,
            ("fail",),
        )
