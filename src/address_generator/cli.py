"""CLI entry point."""

from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console

from address_generator.app import AddressGeneratorApp
from address_generator.config import load_scan_request
from address_generator.prompting import InteractiveRequestBuilder


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        prog="address-generator",
        description=(
            "Generate address activity reports from public extended keys or public addresses."
        ),
    )
    parser.add_argument("--config", type=Path, help="Optional TOML scan configuration file.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Base directory where reports will be written.",
    )
    return parser


def main() -> None:
    """Run the CLI."""

    parser = build_parser()
    args = parser.parse_args()
    console = Console()

    if args.config:
        request = load_scan_request(args.config, output_dir=args.output_dir)
    else:
        request = InteractiveRequestBuilder(console=console).build(output_dir=args.output_dir)

    result = AddressGeneratorApp.create_default().run(request)
    console.print(f"\nOutput written to [bold]{result.output_dir}[/bold]")
