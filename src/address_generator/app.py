"""Application entry point and default dependency wiring."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from address_generator.clients import (
    EsploraAddressProvider,
    EthplorerAddressProvider,
    JsonHttpClient,
    PriceClient,
    ProviderCatalog,
    ProviderRouter,
    SoChainAddressProvider,
)
from address_generator.derivation import (
    AddressDeriver,
    AddressInputLoader,
    ExtendedKeyNormalizer,
)
from address_generator.models import (
    ChainRunResult,
    ChainSymbol,
    DerivedAddress,
    ReportRow,
    RunResult,
    ScanRequest,
    ScanSummary,
    ScanTarget,
)
from address_generator.reporting import ReportWriter
from address_generator.services import PortfolioScanService

ProgressCallback = Callable[[ChainSymbol, int, int, ReportRow | None], None]


class SupportsScanService(Protocol):
    """Protocol for the scan service used by the application facade."""

    def build_rows(
        self,
        target: ScanTarget,
        max_count: int,
        *,
        progress: ProgressCallback | None = None,
    ) -> tuple[ReportRow, ...]:
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
    provider_catalog: ProviderCatalog
    address_deriver: AddressDeriver
    address_input_loader: AddressInputLoader

    @classmethod
    def create_default(cls) -> AddressGeneratorApp:
        """Construct the application with default production dependencies."""

        http_client = JsonHttpClient()
        provider_catalog = ProviderCatalog(
            providers={
                "blockstream-public": EsploraAddressProvider(
                    provider_id="blockstream-public",
                    api_base="https://blockstream.info/api",
                    supported_chains=(ChainSymbol.BTC,),
                    http_client=http_client,
                ),
                "litecoinspace-public": EsploraAddressProvider(
                    provider_id="litecoinspace-public",
                    api_base="https://litecoinspace.org/api",
                    supported_chains=(ChainSymbol.LTC,),
                    http_client=http_client,
                ),
                "sochain": SoChainAddressProvider(http_client=http_client),
                "ethplorer": EthplorerAddressProvider(http_client=http_client),
            }
        )
        scan_service = PortfolioScanService(
            address_deriver=AddressDeriver(ExtendedKeyNormalizer()),
            address_input_loader=AddressInputLoader(),
            price_client=PriceClient(http_client),
            provider_router=ProviderRouter(provider_catalog),
        )
        return cls(
            scan_service=scan_service,
            report_writer=ReportWriter(),
            provider_catalog=provider_catalog,
            address_deriver=scan_service.address_deriver,
            address_input_loader=scan_service.address_input_loader,
        )

    def run(self, request: ScanRequest) -> RunResult:
        """Execute one scan request and write reports."""

        output_dir = self.report_writer.build_output_dir(request.output_dir, request.label)
        result = RunResult(output_dir=output_dir, formats=request.formats, chains={})

        for target in request.targets:
            try:
                rows = self.scan_service.build_rows(target, request.max_count)
                summary = self.scan_service.summarize_rows(rows)
                result.chains[target.chain] = ChainRunResult(
                    rows=rows,
                    summary=summary,
                    providers_tried=tuple(
                        sorted({row.provider_id for row in rows if row.provider_id is not None})
                    ),
                )
            except Exception as exc:
                result.chains[target.chain] = ChainRunResult(rows=(), error=str(exc))

        self.report_writer.write(result)
        return result

    def derive_entries(
        self,
        chain: ChainSymbol,
        public_key: str,
        branches: tuple[int, ...],
        count: int,
    ) -> list[DerivedAddress]:
        """Expose derivation through the application facade."""

        return self.address_deriver.derive_entries(chain, public_key, branches, count)

    def load_addresses(self, value: str, count: int) -> list[str]:
        """Expose address loading through the application facade."""

        return self.address_input_loader.load(value, count)

    def run_with_progress(self, request: ScanRequest, progress: ProgressCallback) -> RunResult:
        """Execute one scan request and surface row-level progress updates."""

        output_dir = self.report_writer.build_output_dir(request.output_dir, request.label)
        result = RunResult(output_dir=output_dir, formats=request.formats, chains={})

        for target in request.targets:
            try:
                rows = self.scan_service.build_rows(target, request.max_count, progress=progress)
                summary = self.scan_service.summarize_rows(rows)
                result.chains[target.chain] = ChainRunResult(
                    rows=rows,
                    summary=summary,
                    providers_tried=tuple(
                        sorted({row.provider_id for row in rows if row.provider_id is not None})
                    ),
                )
            except Exception as exc:
                result.chains[target.chain] = ChainRunResult(rows=(), error=str(exc))

        self.report_writer.write(result)
        return result
