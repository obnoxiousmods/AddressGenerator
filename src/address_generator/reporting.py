"""Filesystem reporting helpers."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from address_generator.formatting import format_decimal, render_report_row, sanitize_label
from address_generator.models import ChainRunResult, ChainSymbol, RunResult


@dataclass
class ReportWriter:
    """Persist chain reports and JSON summaries."""

    def write(self, result: RunResult) -> None:
        """Write all chain outputs for a completed run."""

        result.output_dir.mkdir(parents=True, exist_ok=True)
        for chain, chain_result in result.chains.items():
            if chain_result.error:
                continue
            self._write_chain_files(result.output_dir, chain, chain_result)
        self._write_summary(result)

    def build_output_dir(self, base_output_dir: Path, label: str) -> Path:
        """Build the final output directory path for a label."""

        return base_output_dir / sanitize_label(label)

    def _write_chain_files(
        self,
        output_dir: Path,
        chain: ChainSymbol,
        chain_result: ChainRunResult,
    ) -> None:
        all_lines = [render_report_row(row, chain.value) for row in chain_result.rows]
        active_lines = [
            render_report_row(row, chain.value) for row in chain_result.rows if row.is_active
        ]
        (output_dir / f"{chain.value}_all.txt").write_text(
            "\n".join(all_lines) + ("\n" if all_lines else ""),
            encoding="utf-8",
        )
        (output_dir / f"{chain.value}_active.txt").write_text(
            "\n".join(active_lines) + ("\n" if active_lines else ""),
            encoding="utf-8",
        )

    def _write_summary(self, result: RunResult) -> None:
        payload: dict[str, object] = {"output_dir": str(result.output_dir), "chains": {}}
        chains_payload = payload["chains"]
        assert isinstance(chains_payload, dict)
        for chain, chain_result in result.chains.items():
            if chain_result.error:
                chains_payload[chain.value] = {"error": chain_result.error}
                continue
            assert chain_result.summary is not None
            chains_payload[chain.value] = {
                "total_count": chain_result.summary.total_count,
                "active_count": chain_result.summary.active_count,
                "total_native_balance": format_decimal(
                    chain_result.summary.total_native_balance,
                    8,
                ),
                "total_usd_value": format_decimal(chain_result.summary.total_usd_value, 2),
            }
        (result.output_dir / "summary.json").write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
