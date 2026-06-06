# Usage

## Interactive CLI

```bash
uv run address-generator
```

The CLI prompts for:

1. Output label
2. Address count per chain
3. Enabled chains
4. Input mode per chain
5. Public extended key or public address list

## Config-Driven Runs

```bash
uv run address-generator --config examples/basic-scan.toml
```

## Address Modes

- `xpub`: derive receive addresses from a public extended key
- `addresses`: scan a pasted address list or a file path containing one address per line

## Output Semantics

- `*_all.txt` contains every scanned address
- `*_active.txt` contains addresses with transaction history, balance, or token holdings
- `summary.json` contains aggregate totals
