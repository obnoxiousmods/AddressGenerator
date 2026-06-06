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
BSCSCAN_URL = "https://api.bscscan.com/api"


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

BCH = ChainDefinition(
    api_base="https://bchexplorer.cash/api",
    symbol="BCH",
    coin_gecko_id="bitcoin-cash",
    network={"p2pkh": b"\x00", "p2sh": b"\x05"},
    legacy_versions=frozenset({"xpub", "tpub"}),
    nested_versions=frozenset(),
    native_versions=frozenset(),
    default_mode="legacy",
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

ZEC = ChainDefinition(
    api_base="https://api.zcashinfo.com/api/v1",
    symbol="ZEC",
    coin_gecko_id="zcash",
    network={"p2pkh": b"\x1c\xb8", "p2sh": b"\x1c\xbd"},
    legacy_versions=frozenset({"xpub", "tpub"}),
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

ETC = ChainDefinition(
    api_base="https://etc.blockscout.com/api/v2",
    symbol="ETC",
    coin_gecko_id="ethereum-classic",
    network={},
    legacy_versions=frozenset({"xpub", "tpub"}),
    nested_versions=frozenset(),
    native_versions=frozenset(),
    default_mode="legacy",
)

POL = ChainDefinition(
    api_base="https://polygon.blockscout.com/api/v2",
    symbol="POL",
    coin_gecko_id="matic-network",
    network={},
    legacy_versions=frozenset({"xpub", "tpub"}),
    nested_versions=frozenset(),
    native_versions=frozenset(),
    default_mode="legacy",
)

BSC = ChainDefinition(
    api_base=BSCSCAN_URL,
    symbol="BSC",
    coin_gecko_id="binancecoin",
    network={},
    legacy_versions=frozenset({"xpub", "tpub"}),
    nested_versions=frozenset(),
    native_versions=frozenset(),
    default_mode="legacy",
)

ARB = ChainDefinition(
    api_base="https://arbitrum.blockscout.com/api/v2",
    symbol="ARB",
    coin_gecko_id="ethereum",
    network={},
    legacy_versions=frozenset({"xpub", "tpub"}),
    nested_versions=frozenset(),
    native_versions=frozenset(),
    default_mode="legacy",
)

BASE = ChainDefinition(
    api_base="https://base.blockscout.com/api/v2",
    symbol="BASE",
    coin_gecko_id="ethereum",
    network={},
    legacy_versions=frozenset({"xpub", "tpub"}),
    nested_versions=frozenset(),
    native_versions=frozenset(),
    default_mode="legacy",
)

OP = ChainDefinition(
    api_base="https://optimism.blockscout.com/api/v2",
    symbol="OP",
    coin_gecko_id="ethereum",
    network={},
    legacy_versions=frozenset({"xpub", "tpub"}),
    nested_versions=frozenset(),
    native_versions=frozenset(),
    default_mode="legacy",
)

CHAIN_DEFINITIONS = {
    ChainSymbol.BTC: BTC,
    ChainSymbol.BCH: BCH,
    ChainSymbol.LTC: LTC,
    ChainSymbol.DOGE: DOGE,
    ChainSymbol.ZEC: ZEC,
    ChainSymbol.ETH: ETH,
    ChainSymbol.ETC: ETC,
    ChainSymbol.POL: POL,
    ChainSymbol.BSC: BSC,
    ChainSymbol.ARB: ARB,
    ChainSymbol.BASE: BASE,
    ChainSymbol.OP: OP,
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
    "bch-explorer-public": ProviderMetadata(
        provider_id="bch-explorer-public",
        display_name="BCH Explorer Public API",
        supported_chains=(ChainSymbol.BCH,),
        requires_api_key=False,
        signup_required=False,
        free_tier=True,
        multichain=False,
        reliability=Reliability.PUBLIC_BEST_EFFORT,
        docs_url="https://explorer.bch2.org/docs/api",
        rate_limits="Public API; official docs do not publish a numeric rate limit.",
        notes="Public Bitcoin Cash explorer with Esplora-like address endpoints.",
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
    "zcashinfo-public": ProviderMetadata(
        provider_id="zcashinfo-public",
        display_name="Zcash Info API",
        supported_chains=(ChainSymbol.ZEC,),
        requires_api_key=False,
        signup_required=False,
        free_tier=True,
        multichain=False,
        reliability=Reliability.PUBLIC_DOCUMENTED,
        docs_url="https://api.zcashinfo.com/docs",
        rate_limits="Free tier: 10 requests/s with burst allowance of 30.",
        notes="Transparent-address only. Shielded addresses cannot be queried via the public API.",
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
    "etc-blockscout": ProviderMetadata(
        provider_id="etc-blockscout",
        display_name="Ethereum Classic Blockscout",
        supported_chains=(ChainSymbol.ETC,),
        requires_api_key=False,
        signup_required=False,
        free_tier=True,
        multichain=False,
        reliability=Reliability.PUBLIC_DOCUMENTED,
        docs_url="https://etc.blockscout.com/api-docs",
        rate_limits="Public API; official docs do not publish a numeric rate limit.",
        notes="Public Blockscout instance for Ethereum Classic native balances and tx counts.",
    ),
    "polygon-blockscout": ProviderMetadata(
        provider_id="polygon-blockscout",
        display_name="Polygon Blockscout",
        supported_chains=(ChainSymbol.POL,),
        requires_api_key=False,
        signup_required=False,
        free_tier=True,
        multichain=False,
        reliability=Reliability.PUBLIC_DOCUMENTED,
        docs_url="https://polygon.blockscout.com/api-docs",
        rate_limits="Public API; official docs do not publish a numeric rate limit.",
        notes="Public Blockscout instance for Polygon PoS native balances and tx counts.",
    ),
    "arbitrum-blockscout": ProviderMetadata(
        provider_id="arbitrum-blockscout",
        display_name="Arbitrum Blockscout",
        supported_chains=(ChainSymbol.ARB,),
        requires_api_key=False,
        signup_required=False,
        free_tier=True,
        multichain=False,
        reliability=Reliability.PUBLIC_DOCUMENTED,
        docs_url="https://arbitrum.blockscout.com/api-docs",
        rate_limits="Public API; official docs do not publish a numeric rate limit.",
        notes="Public Blockscout instance for Arbitrum One native balances and tx counts.",
    ),
    "base-blockscout": ProviderMetadata(
        provider_id="base-blockscout",
        display_name="Base Blockscout",
        supported_chains=(ChainSymbol.BASE,),
        requires_api_key=False,
        signup_required=False,
        free_tier=True,
        multichain=False,
        reliability=Reliability.PUBLIC_DOCUMENTED,
        docs_url="https://base.blockscout.com/api-docs",
        rate_limits="Public API; official docs do not publish a numeric rate limit.",
        notes="Public Blockscout instance for Base native balances and tx counts.",
    ),
    "optimism-blockscout": ProviderMetadata(
        provider_id="optimism-blockscout",
        display_name="Optimism Blockscout",
        supported_chains=(ChainSymbol.OP,),
        requires_api_key=False,
        signup_required=False,
        free_tier=True,
        multichain=False,
        reliability=Reliability.PUBLIC_DOCUMENTED,
        docs_url="https://optimism.blockscout.com/api-docs",
        rate_limits="Public API; official docs do not publish a numeric rate limit.",
        notes="Public Blockscout instance for Optimism native balances and tx counts.",
    ),
    "bscscan": ProviderMetadata(
        provider_id="bscscan",
        display_name="BscScan API",
        supported_chains=(ChainSymbol.BSC,),
        requires_api_key=True,
        signup_required=True,
        free_tier=False,
        multichain=False,
        reliability=Reliability.KEYED_DOCUMENTED,
        docs_url="https://docs.bscscan.com/api-endpoints/accounts",
        rate_limits="API key required. Current public docs do not offer anonymous access.",
        notes="Native BNB Smart Chain support with keyed explorer queries.",
    ),
}

DEFAULT_PROVIDER_ORDER = {
    ChainSymbol.BTC: ("blockstream-public", "sochain"),
    ChainSymbol.BCH: ("bch-explorer-public",),
    ChainSymbol.LTC: ("litecoinspace-public", "sochain"),
    ChainSymbol.DOGE: ("sochain",),
    ChainSymbol.ZEC: ("zcashinfo-public",),
    ChainSymbol.ETH: ("ethplorer",),
    ChainSymbol.ETC: ("etc-blockscout",),
    ChainSymbol.POL: ("polygon-blockscout",),
    ChainSymbol.BSC: ("bscscan",),
    ChainSymbol.ARB: ("arbitrum-blockscout",),
    ChainSymbol.BASE: ("base-blockscout",),
    ChainSymbol.OP: ("optimism-blockscout",),
}
