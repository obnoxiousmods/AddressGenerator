"""Lightweight Rich-based TUI runner."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

from address_generator.app import AddressGeneratorApp
from address_generator.models import ChainSymbol, ReportRow, ScanRequest
from address_generator.prompting import InteractiveRequestBuilder


@dataclass
class TuiRunner:
    """Run scans with a lightweight live terminal UI."""

    app: AddressGeneratorApp
    console: Console = field(default_factory=Console)

    def run(self, request: ScanRequest) -> None:
        """Run a request and render live progress."""

        progress_table = Table(title="AddressGenerator TUI")
        progress_table.add_column("Chain")
        progress_table.add_column("Progress")
        progress_table.add_column("Last Address")
        progress_table.add_column("Provider")
        rows_state: dict[ChainSymbol, tuple[int, int, str, str]] = {}

        def on_progress(
            chain: ChainSymbol,
            completed: int,
            total: int,
            row: ReportRow | None,
        ) -> None:
            last_address = "" if row is None else row.address
            provider = "" if row is None or row.provider_id is None else row.provider_id
            rows_state[chain] = (completed, total, last_address, provider)
            progress_table.rows.clear()
            for key, value in rows_state.items():
                progress_table.add_row(key.value, f"{value[0]}/{value[1]}", value[2], value[3])

        output_dir = self.app.report_writer.build_output_dir(request.output_dir, request.label)
        with Live(Group(progress_table), console=self.console, refresh_per_second=8):
            self.app.run_with_progress(request, on_progress)
        self.console.print(Panel.fit(f"Output written to {output_dir}"))

    def run_interactive(self, output_dir: Path) -> None:
        """Collect an interactive request and run it with the TUI."""

        request = InteractiveRequestBuilder(console=self.console).build(output_dir=output_dir)
        self.run(request)
