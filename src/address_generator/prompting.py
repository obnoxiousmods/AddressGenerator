"""Interactive prompt collection."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt

from address_generator.config import parse_formats
from address_generator.formatting import sanitize_label
from address_generator.models import ChainSymbol, InputMode, ScanRequest, ScanTarget


@dataclass
class InteractiveRequestBuilder:
    """Build scan requests from a terminal session."""

    console: Console = field(default_factory=Console)

    def build(self, output_dir: Path) -> ScanRequest:
        """Collect an interactive request."""

        self.console.print("[bold]AddressGenerator[/bold]")
        self.console.print("This project scans only public keys and public addresses.\n")

        label = sanitize_label(Prompt.ask("Output label", default="scan"))
        max_count = IntPrompt.ask("How many addresses per chain", default=25)
        formats = parse_formats(Prompt.ask("Formats csv/json/txt", default="txt,json"))

        targets = []
        for chain in ChainSymbol:
            enabled_by_default = chain in {ChainSymbol.BTC, ChainSymbol.ETH}
            if not Confirm.ask(f"Scan {chain.value}?", default=enabled_by_default):
                continue
            targets.append(self._build_target(chain))

        return ScanRequest(
            label=label,
            max_count=max_count,
            targets=tuple(targets),
            output_dir=output_dir,
            formats=formats,
        )

    def _build_target(self, chain: ChainSymbol) -> ScanTarget:
        """Prompt for a single target."""

        default_mode = "addresses" if chain is ChainSymbol.ETH else "xpub"
        mode = InputMode(
            Prompt.ask(
                f"{chain.value} input mode",
                choices=[InputMode.XPUB.value, InputMode.ADDRESSES.value],
                default=default_mode,
            )
        )
        if mode is InputMode.XPUB:
            value = Prompt.ask(f"Paste {chain.value} public key")
            branches_raw = Prompt.ask("Branches to scan", default="0")
            branches = tuple(int(item.strip()) for item in branches_raw.split(",") if item.strip())
        else:
            value = Prompt.ask(
                f"Paste {chain.value} addresses separated by commas or enter a file path"
            )
            branches = (0,)
        providers_raw = Prompt.ask("Providers override (optional)", default="")
        provider_order = tuple(item.strip() for item in providers_raw.split(",") if item.strip())
        count = IntPrompt.ask("Override address count (0 = use global)", default=0)
        return ScanTarget(
            chain=chain,
            mode=mode,
            value=value.strip(),
            count=None if count == 0 else count,
            branches=branches,
            provider_order=provider_order,
        )
