# AddressGenerator

[![CI](https://github.com/obnoxiousmods/AddressGenerator/actions/workflows/ci.yml/badge.svg)](https://github.com/obnoxiousmods/AddressGenerator/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/github/license/obnoxiousmods/AddressGenerator)](LICENSE)
[![Ruff](https://img.shields.io/badge/lint-ruff-46a2f1.svg)](https://docs.astral.sh/ruff/)
[![Typing](https://img.shields.io/badge/type_checked-ty-9b59b6.svg)](https://github.com/astral-sh/ty)
[![uv](https://img.shields.io/badge/packaging-uv-6bdfdb.svg)](https://docs.astral.sh/uv/)

`AddressGenerator` is a typed, public-key-only Python project for deriving addresses from public extended keys and producing explorer-backed activity reports. It intentionally refuses recovery seeds and passphrases.

## Features

- Interactive CLI and reusable Python API
- `BTC`, `LTC`, `DOGE`, and `ETH` support
- ERC-20 holdings discovery on scanned Ethereum addresses
- `xpub`-style derivation or pasted public address lists
- Per-run `*_all.txt`, `*_active.txt`, and `summary.json` output
- `uv`, `ruff`, `ty`, `pytest`, and coverage-first project setup

## Quick Start

```bash
uv sync --extra dev
uv run address-generator
```

## Example Config

```toml
label = "sample-run"
max_count = 5

[[targets]]
chain = "BTC"
mode = "xpub"
value = "zpub6rFR7y4Q2AijBEqTUquhVz398htDFrtymD9xYYfG1m4wAcvPhXNfE3EfH1r1ADqtfSdVCToUG868RvUUkgDKf31mGDtKsAYz2oz2AGutZYs"

[[targets]]
chain = "ETH"
mode = "addresses"
value = "0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe"
```

Run it:

```bash
uv run address-generator --config examples/basic-scan.toml
```

## Output

Each scan writes to `output/<label>/`:

- `<CHAIN>_all.txt`
- `<CHAIN>_active.txt`
- `summary.json`

Example line:

```text
index=0 | address=bc1q... | txs=4 | balance=0.01500000 BTC | usd=$905.70
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
