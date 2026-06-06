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

## Core Types

- `ScanRequest`
- `ScanTarget`
- `ReportRow`
- `RunResult`
- `ChainSymbol`
- `InputMode`

## Extension Points

- swap `JsonHttpClient` with a custom implementation
- inject fake explorer clients in tests
- use `PortfolioScanService` directly for library-style integration
