# Usage

## Scan Modes

```bash
uv run address-generator scan --config examples/basic-scan.toml
uv run address-generator scan --chain ETH --mode addresses --value "0xabc,0xdef"
uv run address-generator scan --stdin --stdin-format toml < examples/basic-scan.toml
```

`scan` resolves input in this order:

1. `--config`
2. `--stdin`
3. explicit single-target flags
4. interactive prompts

## Interactive CLI

```bash
uv run address-generator scan --interactive
uv run address-generator tui
```

The interactive builder prompts for:

1. Output label
2. Default address count
3. Output formats
4. One or more chain targets
5. Input mode, branches, and provider overrides per target

## Other Commands

```bash
uv run address-generator derive --chain BTC --xpub <XPUB> --branches 0,1 --count 10
uv run address-generator providers --json
uv run address-generator validate --chain BTC --mode xpub --value <XPUB>
uv run address-generator tui --config examples/basic-scan.toml
```

## Address Modes

- `xpub`: derive addresses from a public extended key
- `addresses`: scan pasted addresses, comma-separated addresses, or a file path containing one address per line

## Config Shape

```toml
label = "basic-scan"
max_count = 5
formats = ["txt", "json", "csv"]

[defaults]
branches = [0]
providers = ["blockstream-public"]

[[targets]]
chain = "BTC"
mode = "xpub"
value = "<XPUB>"
branches = [0, 1]
providers = ["blockstream-public", "sochain"]

[[targets]]
chain = "DOGE"
mode = "addresses"
value = "Dabc123...,Ddef456..."
count = 10
```

## Provider Notes

- `BTC` defaults to `blockstream-public`, then `sochain`
- `BCH` defaults to `bch-explorer-public`
- `LTC` defaults to `litecoinspace-public`, then `sochain`
- `DOGE` uses `sochain` for real mainnet support
- `ZEC` uses `zcashinfo-public` for transparent addresses
- `ETH` uses `ethplorer` and includes ERC-20 token notes when present
- `ETC`, `POL`, `ARB`, `BASE`, and `OP` use public `Blockscout` instances
- `BSC` uses keyed `BscScan`

If a keyed provider is configured, set the expected environment variable first:

```bash
export SOCHAIN_API_KEY=your_key_here
export BSCSCAN_API_KEY=your_key_here
```

## Output Semantics

- `*_all.txt` contains every scanned address
- `*_active.txt` contains addresses with transaction history, balance, or token holdings
- matching `json` and `csv` files are written when those formats are enabled
- `summary.json` contains aggregate totals and provider usage
