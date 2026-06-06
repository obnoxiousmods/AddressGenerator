# AddressGenerator

[![CI](https://github.com/obnoxiousmods/AddressGenerator/actions/workflows/ci.yml/badge.svg)](https://github.com/obnoxiousmods/AddressGenerator/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/github/license/obnoxiousmods/AddressGenerator)](LICENSE)
[![Ruff](https://img.shields.io/badge/lint-ruff-46a2f1.svg)](https://docs.astral.sh/ruff/)
[![Typing](https://img.shields.io/badge/type_checked-ty-9b59b6.svg)](https://github.com/astral-sh/ty)
[![uv](https://img.shields.io/badge/packaging-uv-6bdfdb.svg)](https://docs.astral.sh/uv/)

`AddressGenerator` is a typed, public-key-only Python project for deriving addresses
from public extended keys and producing explorer-backed activity reports. It
intentionally refuses recovery seeds and passphrases.

## Features

- Reusable Python API plus `scan`, `derive`, `providers`, `validate`, and `tui` commands
- `BTC`, `BCH`, `LTC`, `DOGE`, `ZEC`, `ETH`, `ETC`, `POL`, `BSC`, `ARB`, `BASE`, and `OP` support
- ERC-20 holdings discovery on scanned Ethereum addresses
- `xpub`-style derivation or pasted public address lists
- `stdin`, interactive prompts, CLI flags, and TOML config support
- `txt`, `json`, and `csv` output formats per run
- Lightweight Rich TUI with live per-chain progress
- Provider routing with chain-specific fallbacks and keyed `DOGE` mainnet support
- `uv`, `ruff`, `ty`, `pytest`, and coverage-first project setup

## Quick Start

```bash
uv sync --extra dev
uv run address-generator scan --config examples/basic-scan.toml
```

## Command Surface

```bash
uv run address-generator scan --config examples/basic-scan.toml
uv run address-generator derive --chain BTC --xpub <XPUB> --count 10 --branches 0,1
uv run address-generator providers --csv
uv run address-generator validate --chain ETH --mode addresses --value "0xabc,0xdef"
uv run address-generator tui --config examples/basic-scan.toml
```

## Example Config

```toml
label = "sample-run"
max_count = 5
formats = ["txt", "json", "csv"]

[defaults]
branches = [0, 1]

[[targets]]
chain = "BTC"
mode = "xpub"
providers = ["blockstream-public", "sochain"]
value = "zpub6rFR7y4Q2AijBEqTUquhVz398htDFrtymD9xYYfG1m4wAcvPhXNfE3EfH1r1ADqtfSdVCToUG868RvUUkgDKf31mGDtKsAYz2oz2AGutZYs"

[[targets]]
chain = "ETH"
mode = "addresses"
value = "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe"
```

Run it:

```bash
uv run address-generator scan --config examples/basic-scan.toml
```

## Output

Each scan writes to `output/<label>/`:

- `<CHAIN>_all.txt`
- `<CHAIN>_active.txt`
- `<CHAIN>_all.json`
- `<CHAIN>_active.json`
- `<CHAIN>_all.csv`
- `<CHAIN>_active.csv`
- `summary.json`

Example line:

```text
index=0 | address=bc1q... | txs=4 | balance=0.01500000 BTC | usd=$905.70
```

## Providers

The default provider catalog is intentionally mixed because there is no single
free, official, multichain backend that cleanly covers all currently
implemented chains.

| Provider | Chains | Signup | Free | Notes |
| --- | --- | --- | --- | --- |
| `blockstream-public` | `BTC` | No | Yes | Good Bitcoin public explorer for prototyping. Official docs do not publish a simple numeric public rate limit. |
| `bch-explorer-public` | `BCH` | No | Yes | Public BCH explorer with Esplora-like address endpoints. |
| `litecoinspace-public` | `LTC` | No | Yes | Litecoin Foundation-run public explorer API. Official docs do not publish a numeric REST rate limit. |
| `sochain` | `BTC`, `LTC`, `DOGE` | Yes | Keyed | Used here for real `DOGE` mainnet support. Requires `SOCHAIN_API_KEY`. |
| `zcashinfo-public` | `ZEC` | No | Yes | Transparent-address API. Free tier is documented at `10 req/s` with burst `30`. |
| `ethplorer` | `ETH` | No | Yes | `freekey` supports `5 req/s`, `50/min`, `200/hour`, `2000/day`, `3000/week`. |
| `etc-blockscout` | `ETC` | No | Yes | Public Blockscout instance for Ethereum Classic. |
| `polygon-blockscout` | `POL` | No | Yes | Public Blockscout instance for Polygon PoS. |
| `arbitrum-blockscout` | `ARB` | No | Yes | Public Blockscout instance for Arbitrum One. |
| `base-blockscout` | `BASE` | No | Yes | Public Blockscout instance for Base. |
| `optimism-blockscout` | `OP` | No | Yes | Public Blockscout instance for Optimism. |
| `bscscan` | `BSC` | Yes | Keyed | Requires `BSCSCAN_API_KEY`. |

Use `uv run address-generator providers` to inspect the current provider metadata
from the installed package.

## Stdin

`scan` can build requests from stdin:

```bash
cat examples/basic-scan.toml | uv run address-generator scan --stdin --stdin-format toml
printf '0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe\n' | \
  uv run address-generator scan --stdin --stdin-format addresses --chain ETH --mode addresses
```

## Why No Seed Input?

This project does not process secret wallet material. It is designed for public derivation inputs only:

- public extended keys such as `xpub`, `ypub`, `zpub`, `Ltub`, `Mtub`, or `dgub`
- public address lists

That boundary is deliberate.

## Documentation

- [Usage Guide](docs/usage.md)
- [Architecture](docs/architecture.md)
- [API Guide](docs/api.md)
- [Development](docs/development.md)
- [Security Policy](SECURITY.md)
- [Contributing](CONTRIBUTING.md)

## Development

```bash
uv sync --extra dev
uv run ruff check .
uv run ruff format --check .
uv run ty check
uv run pytest
```
