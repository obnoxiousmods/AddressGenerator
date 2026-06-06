"""CLI entry point."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from rich.console import Console
from rich.table import Table

from address_generator.app import AddressGeneratorApp
from address_generator.config import load_scan_request, parse_formats
from address_generator.models import ChainSymbol, InputMode, ScanRequest, ScanTarget, StdinFormat
from address_generator.prompting import InteractiveRequestBuilder
from address_generator.stdin_loader import load_request_from_stdin
from address_generator.tui import TuiRunner


def build_parser() -> argparse.ArgumentParser:
    """Create the command-line parser."""

    parser = argparse.ArgumentParser(
        prog="address-generator",
        description=(
            "Generate address activity reports from public extended keys "
            "or public addresses."
        ),
    )
    subparsers = parser.add_subparsers(dest="command", required=False)

    scan = subparsers.add_parser("scan", help="Run a scan request.")
    scan.add_argument("--config", type=Path, help="Optional TOML scan configuration file.")
    scan.add_argument("--stdin", action="store_true", help="Read request or addresses from stdin.")
    scan.add_argument(
        "--stdin-format",
        choices=[item.value for item in StdinFormat],
        default=StdinFormat.JSON.value,
        help="How to interpret stdin when --stdin is used.",
    )
    scan.add_argument(
        "--label",
        default="scan",
        help="Run label when building a request from flags.",
    )
    scan.add_argument("--count", type=int, default=25, help="Default address count per chain.")
    scan.add_argument(
        "--chain",
        choices=[item.value for item in ChainSymbol],
        help="Single-chain flag mode.",
    )
    scan.add_argument(
        "--mode",
        choices=[item.value for item in InputMode],
        help="Single-target input mode.",
    )
    scan.add_argument("--value", help="Single-target xpub or address list.")
    scan.add_argument(
        "--branches",
        default="0",
        help="Comma-separated branch indexes for xpub scans.",
    )
    scan.add_argument(
        "--provider",
        action="append",
        default=[],
        help="Provider override(s) in priority order.",
    )
    scan.add_argument("--format", default="txt,json", help="Comma-separated output formats.")
    scan.add_argument("--output-dir", type=Path, default=Path("output"))
    scan.add_argument("--interactive", action="store_true", help="Force interactive prompt mode.")

    derive = subparsers.add_parser("derive", help="Derive addresses from a public xpub-style key.")
    derive.add_argument("--chain", required=True, choices=[item.value for item in ChainSymbol])
    derive.add_argument("--xpub", required=True)
    derive.add_argument("--count", type=int, default=10)
    derive.add_argument("--branches", default="0")
    derive.add_argument("--json", action="store_true")

    providers = subparsers.add_parser("providers", help="List configured activity providers.")
    providers.add_argument("--json", action="store_true")
    providers.add_argument("--csv", action="store_true")

    validate = subparsers.add_parser("validate", help="Validate scan input.")
    validate.add_argument("--chain", required=True, choices=[item.value for item in ChainSymbol])
    validate.add_argument("--mode", required=True, choices=[item.value for item in InputMode])
    validate.add_argument("--value", required=True)
    validate.add_argument("--count", type=int, default=1)

    tui = subparsers.add_parser("tui", help="Run the lightweight TUI.")
    tui.add_argument("--config", type=Path)
    tui.add_argument("--output-dir", type=Path, default=Path("output"))

    return parser


def main() -> None:
    """Run the CLI."""

    parser = build_parser()
    args = parser.parse_args()
    console = Console()
    app = AddressGeneratorApp.create_default()
    command = args.command or "scan"

    if command == "providers":
        _run_providers(app, console, args.json, args.csv)
        return
    if command == "derive":
        _run_derive(app, console, args)
        return
    if command == "validate":
        _run_validate(app, console, args)
        return
    if command == "tui":
        _run_tui(app, args)
        return

    request = _build_scan_request(args, console)
    result = app.run(request)
    console.print(f"\nOutput written to [bold]{result.output_dir}[/bold]")


def _build_scan_request(args: argparse.Namespace, console: Console) -> ScanRequest:
    if args.config:
        return load_scan_request(args.config, output_dir=args.output_dir)
    if args.stdin:
        payload = sys.stdin.read()
        chain = None if args.chain is None else ChainSymbol(args.chain)
        mode = None if args.mode is None else InputMode(args.mode)
        return load_request_from_stdin(
            payload,
            stdin_format=StdinFormat(args.stdin_format),
            output_dir=args.output_dir,
            label=args.label,
            max_count=args.count,
            chain=chain,
            mode=mode,
            formats=tuple(part.strip() for part in args.format.split(",") if part.strip()),
        )
    if args.chain and args.mode and args.value:
        branches = tuple(int(item.strip()) for item in args.branches.split(",") if item.strip())
        return ScanRequest(
            label=args.label,
            max_count=args.count,
            targets=(
                ScanTarget(
                    chain=ChainSymbol(args.chain),
                    mode=InputMode(args.mode),
                    value=args.value,
                    branches=branches,
                    provider_order=tuple(args.provider),
                ),
            ),
            output_dir=args.output_dir,
            formats=parse_formats(args.format),
        )
    return InteractiveRequestBuilder(console=console).build(output_dir=args.output_dir)


def _run_derive(app: AddressGeneratorApp, console: Console, args: argparse.Namespace) -> None:
    chain = ChainSymbol(args.chain)
    branches = tuple(int(item.strip()) for item in args.branches.split(",") if item.strip())
    entries = app.derive_entries(chain, args.xpub, branches, args.count)
    payload = [
        {
            "branch": item.branch,
            "index": item.index,
            "path_label": item.path_label,
            "address": item.address,
        }
        for item in entries
    ]
    if args.json:
        console.print_json(json.dumps(payload))
        return
    table = Table(title=f"Derived {chain.value} Addresses")
    table.add_column("Path")
    table.add_column("Address")
    for item in payload:
        table.add_row(str(item["path_label"]), str(item["address"]))
    console.print(table)


def _run_providers(
    app: AddressGeneratorApp,
    console: Console,
    as_json: bool,
    as_csv: bool,
) -> None:
    metadata = app.provider_catalog.list_metadata()
    if as_json:
        console.print_json(json.dumps([item.__dict__ for item in metadata], default=str))
        return
    if as_csv:
        console.print(app.provider_catalog.describe_as_csv())
        return
    table = Table(title="Configured Providers")
    table.add_column("Provider")
    table.add_column("Chains")
    table.add_column("API Key")
    table.add_column("Free")
    table.add_column("Rate Limits")
    table.add_column("Docs")
    for item in metadata:
        table.add_row(
            item.display_name,
            ",".join(chain.value for chain in item.supported_chains),
            "yes" if item.requires_api_key else "no",
            "yes" if item.free_tier else "no",
            item.rate_limits,
            item.docs_url,
        )
    console.print(table)


def _run_validate(app: AddressGeneratorApp, console: Console, args: argparse.Namespace) -> None:
    chain = ChainSymbol(args.chain)
    mode = InputMode(args.mode)
    if mode is InputMode.XPUB:
        derived = app.derive_entries(chain, args.value, (0,), args.count)
        console.print(f"valid xpub-style input; first derived address: {derived[0].address}")
        return
    addresses = app.load_addresses(args.value, args.count)
    console.print(f"loaded {len(addresses)} address(es)")


def _run_tui(app: AddressGeneratorApp, args: argparse.Namespace) -> None:
    runner = TuiRunner(app)
    if args.config:
        runner.run(load_scan_request(args.config, output_dir=args.output_dir))
    else:
        runner.run_interactive(args.output_dir)
