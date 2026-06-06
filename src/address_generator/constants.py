"""Project constants and chain definitions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

SATOSHI = Decimal("100000000")
WEI = Decimal("1000000000000000000")
SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
ETHPLORER_URL = "https://api.ethplorer.io/getAddressInfo/{address}"


@dataclass(frozen=True)
class ChainDefinition:
    """Static chain configuration for derivation and explorer routing."""

    api_base: str
    symbol: str
    coin_gecko_id: str | None
    network: dict[str, bytes | str]
    legacy_versions: frozenset[str]
    nested_versions: frozenset[str]
    native_versions: frozenset[str]
    default_mode: str


BTC = ChainDefinition(
    api_base="https://blockstream.info/api",
    symbol="BTC",
    coin_gecko_id="bitcoin",
    network={"p2pkh": b"\x00", "p2sh": b"\x05", "bech32": "bc"},
    legacy_versions=frozenset({"xpub", "tpub"}),
    nested_versions=frozenset({"ypub", "upub"}),
    native_versions=frozenset({"zpub", "vpub"}),
    default_mode="native",
)

LTC = ChainDefinition(
    api_base="https://litecoinspace.org/api",
    symbol="LTC",
    coin_gecko_id="litecoin",
    network={"p2pkh": b"\x30", "p2sh": b"\x32", "bech32": "ltc"},
    legacy_versions=frozenset({"xpub", "tpub", "Ltub", "Mtub"}),
    nested_versions=frozenset({"ypub", "upub", "Mtub"}),
    native_versions=frozenset({"zpub", "vpub"}),
    default_mode="native",
)

DOGE = ChainDefinition(
    api_base="https://explorer.dogecoinev.com/api",
    symbol="DOGE",
    coin_gecko_id="dogecoin",
    network={"p2pkh": b"\x1e", "p2sh": b"\x16"},
    legacy_versions=frozenset({"xpub", "tpub", "dgub"}),
    nested_versions=frozenset(),
    native_versions=frozenset(),
    default_mode="legacy",
)

ETH = ChainDefinition(
    api_base="https://api.ethplorer.io",
    symbol="ETH",
    coin_gecko_id="ethereum",
    network={},
    legacy_versions=frozenset({"xpub", "tpub"}),
    nested_versions=frozenset(),
    native_versions=frozenset(),
    default_mode="legacy",
)
