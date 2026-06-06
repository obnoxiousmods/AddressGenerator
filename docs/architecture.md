# Architecture

`AddressGenerator` is split into a few focused layers:

- `models.py`: typed domain models and enums
- `api_types.py`: `TypedDict` shapes for external API payloads
- `clients.py`: HTTP-backed pricing, provider metadata, explorer clients, and provider routing
- `derivation.py`: public key normalization and address derivation
- `services.py`: orchestration for derivation and scanning
- `reporting.py`: filesystem output
- `config.py`: TOML config loader
- `stdin_loader.py`: JSON/TOML/raw-address stdin decoding
- `prompting.py`: interactive CLI collection
- `tui.py`: live Rich UI wrapper
- `cli.py`: argparse entry point and command dispatch

## Provider Model

Explorer access is intentionally abstracted behind two reusable layers:

- `ProviderCatalog`: owns configured provider instances and descriptive metadata
- `ProviderRouter`: resolves provider order for a chain and tries fallbacks in sequence

That design lets the package mix:

- public explorer APIs for fast no-signup prototyping
- keyed providers where mainnet coverage requires them
- test doubles for deterministic CI

The currently implemented chain families are:

- UTXO: `BTC`, `BCH`, `LTC`, `DOGE`, `ZEC`
- EVM mainnet/L2 family: `ETH`, `ETC`, `POL`, `BSC`, `ARB`, `BASE`, `OP`

## Execution Flow

1. The CLI or TUI builds a `ScanRequest`.
2. `AddressGeneratorApp` hands each target to `PortfolioScanService`.
3. The service derives or loads public addresses.
4. `PriceClient` fetches USD spot prices.
5. `ProviderRouter` asks providers for address activity.
6. `ReportWriter` emits `txt`, `json`, and `csv` outputs plus `summary.json`.

The design keeps explorer I/O and derivation logic injectable so tests can cover
realistic behavior without live network access.
