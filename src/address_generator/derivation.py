"""Public-key normalization and address derivation services."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import cast

from embit import bip32, script
from eth_hash.auto import keccak

from address_generator.constants import (
    ARB,
    BASE,
    BCH,
    BSC,
    BTC,
    DOGE,
    ETC,
    ETH,
    LTC,
    OP,
    POL,
    SECP256K1_P,
    ZEC,
)
from address_generator.exceptions import ConfigurationError
from address_generator.models import ChainSymbol, DerivedAddress

CHAIN_MAP = {
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


@dataclass(frozen=True)
class ExtendedKeyNormalizer:
    """Normalize chain-specific extended-key prefixes into embit-compatible variants."""

    replacements: dict[str, str] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "replacements",
            self.replacements or {"Ltub": "xpub", "Mtub": "ypub", "dgub": "xpub"},
        )

    def normalize(self, public_key: str) -> str:
        """Return a normalized extended public key string."""

        assert self.replacements is not None
        prefix = public_key[:4]
        replacement = self.replacements.get(prefix)
        if replacement is None:
            return public_key

        raw = bip32.base58.decode_check(public_key)
        version = bip32.NETWORKS["main"][replacement]
        return bip32.base58.encode_check(cast(bytes, version) + raw[4:])


@dataclass(frozen=True)
class AddressInputLoader:
    """Load public addresses from inline input or from a file."""

    def load(self, value: str, max_count: int) -> list[str]:
        """Load up to ``max_count`` public addresses."""

        path = Path(value).expanduser()
        if path.exists():
            addresses = [
                line.strip()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip()
            ]
            return addresses[:max_count]
        return [part.strip() for part in value.split(",") if part.strip()][:max_count]


@dataclass(frozen=True)
class AddressDeriver:
    """Derive chain-specific addresses from a public extended key."""

    normalizer: ExtendedKeyNormalizer

    def derive(self, chain: ChainSymbol, public_key: str, max_count: int) -> list[str]:
        """Derive receive addresses for a supported chain."""

        return [item.address for item in self.derive_entries(chain, public_key, (0,), max_count)]

    def derive_entries(
        self,
        chain: ChainSymbol,
        public_key: str,
        branches: tuple[int, ...],
        max_count: int,
    ) -> list[DerivedAddress]:
        """Derive receive addresses and include branch/index metadata."""

        normalized_key = self.normalizer.normalize(public_key.strip())
        hdkey = bip32.HDKey.from_string(normalized_key)

        if chain in {
            ChainSymbol.ETH,
            ChainSymbol.ETC,
            ChainSymbol.POL,
            ChainSymbol.BSC,
            ChainSymbol.ARB,
            ChainSymbol.BASE,
            ChainSymbol.OP,
        }:
            return [
                DerivedAddress(
                    branch=branch,
                    index=index,
                    path_label=f"{branch}/{index}",
                    address=self._derive_eth_address(hdkey, branch, index),
                )
                for branch in branches
                for index in range(max_count)
            ]

        chain_definition = CHAIN_MAP[chain]
        mode = self._infer_script_mode(chain, public_key)
        derived: list[DerivedAddress] = []
        for branch in branches:
            for index in range(max_count):
                public_child_key = hdkey.derive([branch, index]).key
                if mode == "legacy":
                    address = script.p2pkh(public_child_key).address(chain_definition.network)
                elif mode == "nested":
                    address = script.p2sh(script.p2wpkh(public_child_key).script()).address(
                        chain_definition.network
                    )
                else:
                    address = script.p2wpkh(public_child_key).address(chain_definition.network)
                derived.append(
                    DerivedAddress(
                        branch=branch,
                        index=index,
                        path_label=f"{branch}/{index}",
                        address=address,
                    )
                )
        return derived

    def _infer_script_mode(self, chain: ChainSymbol, public_key: str) -> str:
        """Infer the script family from the extended-key prefix."""

        prefix = public_key[:4]
        chain_definition = CHAIN_MAP[chain]
        if prefix in chain_definition.legacy_versions:
            return "legacy"
        if prefix in chain_definition.nested_versions:
            return "nested"
        if prefix in chain_definition.native_versions:
            return "native"
        return chain_definition.default_mode

    def _derive_eth_address(self, hdkey: bip32.HDKey, branch: int, index: int) -> str:
        """Derive an EVM address from an uncompressed public key hash."""

        compressed_sec = hdkey.derive([branch, index]).key.sec()
        prefix = compressed_sec[0]
        x_coordinate = int.from_bytes(compressed_sec[1:], "big")
        y_square = (pow(x_coordinate, 3, SECP256K1_P) + 7) % SECP256K1_P
        y_coordinate = pow(y_square, (SECP256K1_P + 1) // 4, SECP256K1_P)
        if (y_coordinate & 1) != (prefix & 1):
            y_coordinate = SECP256K1_P - y_coordinate

        public_key = x_coordinate.to_bytes(32, "big") + y_coordinate.to_bytes(32, "big")
        return "0x" + keccak(public_key)[-20:].hex()


def ensure_positive_count(max_count: int) -> None:
    """Raise when a count is not positive."""

    if max_count <= 0:
        raise ConfigurationError("max_count must be greater than zero.")
