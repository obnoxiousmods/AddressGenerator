# Architecture

`AddressGenerator` is split into a few focused layers:

- `models.py`: typed domain models and enums
- `api_types.py`: `TypedDict` shapes for external API payloads
- `clients.py`: HTTP-backed pricing and explorer clients
- `derivation.py`: public key normalization and address derivation
- `services.py`: orchestration for derivation and scanning
- `reporting.py`: filesystem output
- `config.py`: TOML config loader
- `prompting.py`: interactive CLI collection
- `cli.py`: argparse entry point

The design keeps explorer I/O and derivation logic injectable so tests can cover realistic behavior without live network access.
