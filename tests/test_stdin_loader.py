from __future__ import annotations

from pathlib import Path

from address_generator.models import ChainSymbol, InputMode, StdinFormat
from address_generator.stdin_loader import load_request_from_stdin


def test_load_request_from_stdin_json() -> None:
    request = load_request_from_stdin(
        '{"label":"demo","max_count":2,"targets":[{"chain":"ETH","mode":"addresses","value":"0xabc"}]}',
        stdin_format=StdinFormat.JSON,
        output_dir=Path("out"),
    )
    assert request.label == "demo"
    assert request.targets[0].chain is ChainSymbol.ETH


def test_load_request_from_stdin_toml() -> None:
    request = load_request_from_stdin(
        (
            'label = "demo"\n'
            "max_count = 1\n\n"
            "[[targets]]\n"
            'chain = "BTC"\n'
            'mode = "addresses"\n'
            'value = "bc1"\n'
        ),
        stdin_format=StdinFormat.TOML,
        output_dir=Path("out"),
    )
    assert request.targets[0].value == "bc1"


def test_load_request_from_stdin_addresses_uses_defaults() -> None:
    request = load_request_from_stdin(
        "a\nb\n",
        stdin_format=StdinFormat.ADDRESSES,
        output_dir=Path("out"),
        chain=ChainSymbol.DOGE,
        mode=InputMode.ADDRESSES,
        formats=("txt", "csv"),
    )
    assert request.label == "stdin-scan"
    assert request.targets[0].chain is ChainSymbol.DOGE
    assert tuple(item.value for item in request.formats) == ("txt", "csv")
