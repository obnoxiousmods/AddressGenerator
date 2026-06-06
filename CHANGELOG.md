# Changelog

## 0.3.0

- Added subcommands for `scan`, `derive`, `providers`, `validate`, and `tui`.
- Added stdin-driven request loading for JSON, TOML, and raw address lists.
- Added provider metadata, per-chain provider ordering, and provider fallback routing.
- Replaced the incorrect DogecoinEV integration with keyed `SoChain` support for real `DOGE` mainnet.
- Added `txt`, `json`, and `csv` report emission per chain.
- Added live TUI progress rendering.
- Expanded tests to cover CLI dispatch, provider routing, stdin parsing, app helpers, and TUI behavior.

## 0.4.0

- Added `BCH`, `ZEC`, `ETC`, `POL`, `BSC`, `ARB`, `BASE`, and `OP`.
- Added public `BCH` explorer support and documented public `ZEC` support.
- Added public `Blockscout` providers for `ETC`, `Polygon`, `Arbitrum`, `Base`, and `Optimism`.
- Added keyed `BscScan` support for `BSC`.

## 0.2.0

- Refactored the project into a typed `src/` layout.
- Added reusable service, client, derivation, and reporting classes.
- Added `uv`, `ruff`, `ty`, `pytest`, and coverage configuration.
- Added GitHub workflow, templates, docs, examples, and a broader test suite.

## 0.1.0

- Initial single-file prototype.
