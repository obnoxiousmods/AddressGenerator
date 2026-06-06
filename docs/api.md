# API Guide

## Primary Entry Point

```python
from pathlib import Path

from address_generator.app import AddressGeneratorApp
from address_generator.config import load_scan_request

request = load_scan_request(Path("examples/basic-scan.toml"))
app = AddressGeneratorApp.create_default()
result = app.run(request)
print(result.output_dir)
```

## Programmatic Request Construction

```python
from pathlib import Path

from address_generator.app import AddressGeneratorApp
from address_generator.models import ChainSymbol, InputMode, ScanRequest, ScanTarget

app = AddressGeneratorApp.create_default()
request = ScanRequest(
    label="eth-watch",
    max_count=5,
    output_dir=Path("output"),
    targets=(
        ScanTarget(
            chain=ChainSymbol.ETH,
            mode=InputMode.ADDRESSES,
            value="0xde0B295669a9FD93d5F28D9Ec85E40f4cb697BAe",
        ),
    ),
)
result = app.run(request)
```

## Core Types

- `ScanRequest`
- `ScanTarget`
- `ReportRow`
- `RunResult`
- `ChainSymbol`
- `InputMode`

## Facade Helpers

`AddressGeneratorApp` also exposes smaller building blocks for integration code:

- `derive_entries(chain, public_key, branches, count)`
- `load_addresses(value, count)`
- `run_with_progress(request, callback)`

## Extension Points

- swap `JsonHttpClient` with a custom implementation
- inject custom provider instances into `ProviderCatalog`
- use `ProviderRouter` to define provider precedence and fallback behavior
- inject fake explorer clients in tests
- use `PortfolioScanService` directly for library-style integration
