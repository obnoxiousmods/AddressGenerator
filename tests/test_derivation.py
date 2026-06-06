from __future__ import annotations

from pathlib import Path

import pytest

from address_generator.derivation import (
    AddressDeriver,
    AddressInputLoader,
    ExtendedKeyNormalizer,
    ensure_positive_count,
)
from address_generator.exceptions import ConfigurationError
from address_generator.models import ChainSymbol


def test_normalize_ltub_prefix(normalizer: ExtendedKeyNormalizer) -> None:
    assert normalizer.normalize("xpub123") == "xpub123"


def test_normalizer_handles_dgub_prefix(normalizer: ExtendedKeyNormalizer) -> None:
    assert normalizer.replacements is not None
    assert normalizer.replacements["dgub"] == "xpub"


def test_load_addresses_from_inline(address_loader: AddressInputLoader) -> None:
    addresses = address_loader.load("a, b, c", 2)
    assert addresses == ["a", "b"]


def test_load_addresses_from_file(address_loader: AddressInputLoader, tmp_path: Path) -> None:
    path = tmp_path / "addresses.txt"
    path.write_text("one\ntwo\n", encoding="utf-8")
    addresses = address_loader.load(str(path), 10)
    assert addresses == ["one", "two"]


def test_derive_btc_bech32_addresses(address_deriver: AddressDeriver) -> None:
    zpub = (
        "zpub6rFR7y4Q2AijBEqTUquhVz398htDFrtymD9xYYfG1m4wAcvPhXNfE3EfH1r1"
        "ADqtfSdVCToUG868RvUUkgDKf31mGDtKsAYz2oz2AGutZYs"
    )
    addresses = address_deriver.derive(ChainSymbol.BTC, zpub, 2)
    assert addresses == [
        "bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu",
        "bc1qnjg0jd8228aq7egyzacy8cys3knf9xvrerkf9g",
    ]


def test_derive_eth_addresses(address_deriver: AddressDeriver) -> None:
    xpub = (
        "xpub6DCoCpSuQZB2jawqnGMEPS63ePKWkwWPH4TU45Q7LPXWuNd8TMtVxRrgjtEsh"
        "uqpK3mdhaWHPFsBngh5GFZaM6si3yZdUsT8ddYM3PwnATt"
    )
    addresses = address_deriver.derive(ChainSymbol.ETH, xpub, 2)
    assert addresses == [
        "0x9858effd232b4033e47d90003d41ec34ecaeda94",
        "0x6fac4d18c912343bf86fa7049364dd4e424ab9c0",
    ]


def test_derive_entries_include_branch_labels(address_deriver: AddressDeriver) -> None:
    zpub = (
        "zpub6rFR7y4Q2AijBEqTUquhVz398htDFrtymD9xYYfG1m4wAcvPhXNfE3EfH1r1"
        "ADqtfSdVCToUG868RvUUkgDKf31mGDtKsAYz2oz2AGutZYs"
    )
    entries = address_deriver.derive_entries(ChainSymbol.BTC, zpub, (0, 1), 1)
    assert entries[0].path_label == "0/0"
    assert entries[1].path_label == "1/0"


def test_derive_bch_legacy_address_prefix(address_deriver: AddressDeriver) -> None:
    zpub = (
        "zpub6rFR7y4Q2AijBEqTUquhVz398htDFrtymD9xYYfG1m4wAcvPhXNfE3EfH1r1"
        "ADqtfSdVCToUG868RvUUkgDKf31mGDtKsAYz2oz2AGutZYs"
    )
    address = address_deriver.derive(ChainSymbol.BCH, zpub, 1)[0]
    assert address.startswith("1")


def test_derive_zec_transparent_address_prefix(address_deriver: AddressDeriver) -> None:
    zpub = (
        "zpub6rFR7y4Q2AijBEqTUquhVz398htDFrtymD9xYYfG1m4wAcvPhXNfE3EfH1r1"
        "ADqtfSdVCToUG868RvUUkgDKf31mGDtKsAYz2oz2AGutZYs"
    )
    address = address_deriver.derive(ChainSymbol.ZEC, zpub, 1)[0]
    assert address.startswith("t1")


def test_derive_blockscout_evm_addresses(address_deriver: AddressDeriver) -> None:
    zpub = (
        "zpub6rFR7y4Q2AijBEqTUquhVz398htDFrtymD9xYYfG1m4wAcvPhXNfE3EfH1r1"
        "ADqtfSdVCToUG868RvUUkgDKf31mGDtKsAYz2oz2AGutZYs"
    )
    for chain in (ChainSymbol.ETC, ChainSymbol.POL, ChainSymbol.BSC, ChainSymbol.ARB):
        address = address_deriver.derive(chain, zpub, 1)[0]
        assert address.startswith("0x")


def test_ensure_positive_count_rejects_zero() -> None:
    with pytest.raises(ConfigurationError):
        ensure_positive_count(0)
