"""Project constants and chain definitions."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from address_generator.models import ChainSymbol, ProviderMetadata, Reliability

SATOSHI = Decimal("100000000")
WEI = Decimal("1000000000000000000")
SECP256K1_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"
ETHPLORER_URL = "https://api.ethplorer.io/getAddressInfo/{address}"
SOCHAIN_URL = "https://chain.so/api/v3"


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
    api_base=SOCHAIN_URL,
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

CHAIN_DEFINITIONS = {
    ChainSymbol.BTC: BTC,
    ChainSymbol.LTC: LTC,
    ChainSymbol.DOGE: DOGE,
    ChainSymbol.ETH: ETH,
}

PROVIDER_METADATA = {
    "blockstream-public": ProviderMetadata(
        provider_id="blockstream-public",
        display_name="Blockstream Public Explorer",
        supported_chains=(ChainSymbol.BTC,),
        requires_api_key=False,
        signup_required=False,
        free_tier=True,
        multichain=False,
        reliability=Reliability.PUBLIC_DOCUMENTED,
        docs_url="https://blockstream.info/explorer-api",
        rate_limits=(
            "Public/free tier with rate limits suitable for individual use and "
            "prototyping; no official numeric public limit published."
        ),
        notes=(
            "Good for Bitcoin prototyping. Paid Explorer API exists for higher "
            "reliability and API keys."
        ),
    ),
    "litecoinspace-public": ProviderMetadata(
        provider_id="litecoinspace-public",
        display_name="Litecoin Space Public API",
        supported_chains=(ChainSymbol.LTC,),
        requires_api_key=False,
        signup_required=False,
        free_tier=True,
        multichain=False,
        reliability=Reliability.PUBLIC_DOCUMENTED,
        docs_url="https://litecoinspace.org/docs/api/rest",
        rate_limits="Public API; official docs do not publish a numeric REST rate limit.",
        notes="Litecoin Foundation-operated public explorer API for Litecoin.",
    ),
    "sochain": ProviderMetadata(
        provider_id="sochain",
        display_name="SoChain API",
        supported_chains=(ChainSymbol.BTC, ChainSymbol.LTC, ChainSymbol.DOGE),
        requires_api_key=True,
        signup_required=True,
        free_tier=False,
        multichain=True,
        reliability=Reliability.KEYED_DOCUMENTED,
        docs_url="https://chain.so/api",
        rate_limits=(
            "API key required. Docs require login/sign up; current public docs "
            "do not state a simple anonymous free tier."
        ),
        notes=(
            "Use for real Dogecoin mainnet support in this project. Also usable "
            "as a keyed fallback for BTC/LTC."
        ),
    ),
    "ethplorer": ProviderMetadata(
        provider_id="ethplorer",
        display_name="Ethplorer API",
        supported_chains=(ChainSymbol.ETH,),
        requires_api_key=False,
        signup_required=False,
        free_tier=True,
        multichain=False,
        reliability=Reliability.PUBLIC_DOCUMENTED,
        docs_url="https://ethplorer.zendesk.com/hc/en-us/articles/900000907706-API-Keys-Limits",
        rate_limits=(
            "freekey: 5 req/s, 50/min, 200/hour, 2000/day, 3000/week. "
            "Free personal key: 10 req/s."
        ),
        notes=(
            "Convenient for ETH and ERC-20 discovery. freekey is explicitly not "
            "recommended for product mode."
        ),
    ),
}

DEFAULT_PROVIDER_ORDER = {
    ChainSymbol.BTC: ("blockstream-public", "sochain"),
    ChainSymbol.LTC: ("litecoinspace-public", "sochain"),
    ChainSymbol.DOGE: ("sochain",),
    ChainSymbol.ETH: ("ethplorer",),
}
