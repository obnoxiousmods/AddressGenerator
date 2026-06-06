"""Application entry point and default dependency wiring."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from address_generator.clients import (
    EthereumExplorerClient,
    JsonHttpClient,
    PriceClient,
    UtxoExplorerClient,
)
from address_generator.derivation import (
    AddressDeriver,
    AddressInputLoader,
    ExtendedKeyNormalizer,
)
from address_generator.models import (
    ChainRunResult,
    ReportRow,
    RunResult,
    ScanRequest,
    ScanSummary,
    ScanTarget,
)
from address_generator.reporting import ReportWriter
from address_generator.services import PortfolioScanService


class SupportsScanService(Protocol):
    """Protocol for the scan service used by the application facade."""

    def build_rows(self, target: ScanTarget, max_count: int) -> tuple[ReportRow, ...]:
        """Build rows for a single target."""

    def summarize_rows(self, rows: tuple[ReportRow, ...]) -> ScanSummary:
        """Summarize rows for a single target."""


class SupportsReportWriter(Protocol):
    """Protocol for the report writer used by the application facade."""

    def build_output_dir(self, base_output_dir: Path, label: str) -> Path:
        """Return the output directory for a run."""

    def write(self, result: RunResult) -> None:
        """Persist a run result."""


@dataclass
class AddressGeneratorApp:
    """High-level facade used by the CLI and programmatic consumers."""

    scan_service: SupportsScanService
    report_writer: SupportsReportWriter

    @classmethod
    def create_default(cls) -> AddressGeneratorApp:
        """Construct the application with default production dependencies."""

        http_client = JsonHttpClient()
        scan_service = PortfolioScanService(
            address_deriver=AddressDeriver(ExtendedKeyNormalizer()),
            address_input_loader=AddressInputLoader(),
            price_client=PriceClient(http_client),
            utxo_explorer_client=UtxoExplorerClient(http_client),
            ethereum_explorer_client=EthereumExplorerClient(http_client),
        )
        return cls(scan_service=scan_service, report_writer=ReportWriter())

    def run(self, request: ScanRequest) -> RunResult:
        """Execute one scan request and write reports."""

        output_dir = self.report_writer.build_output_dir(request.output_dir, request.label)
        result = RunResult(output_dir=output_dir, chains={})

        for target in request.targets:
            try:
                rows = self.scan_service.build_rows(target, request.max_count)
                summary = self.scan_service.summarize_rows(rows)
                result.chains[target.chain] = ChainRunResult(rows=rows, summary=summary)
            except Exception as exc:
                result.chains[target.chain] = ChainRunResult(rows=(), error=str(exc))

        self.report_writer.write(result)
        return result
