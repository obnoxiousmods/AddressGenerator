from __future__ import annotations

from pathlib import Path

import pytest
from rich.console import Console
from rich.prompt import Confirm, IntPrompt, Prompt

from address_generator.prompting import InteractiveRequestBuilder


def test_prompt_builder_instantiates() -> None:
    builder = InteractiveRequestBuilder(console=Console(record=True))
    assert builder.console is not None


def test_prompt_builder_collects_request(monkeypatch: pytest.MonkeyPatch) -> None:
    prompt_values = iter(
        [
            "demo",
            "txt,json",
            "addresses",
            "bc1qinline",
            "",
            "addresses",
            "0xabc",
            "",
        ]
    )
    confirm_values = iter([True, False, False, True])

    monkeypatch.setattr(Prompt, "ask", lambda *args, **kwargs: next(prompt_values))
    int_values = iter([2, 0, 0])
    monkeypatch.setattr(IntPrompt, "ask", lambda *args, **kwargs: next(int_values))
    monkeypatch.setattr(Confirm, "ask", lambda *args, **kwargs: next(confirm_values))

    request = InteractiveRequestBuilder(console=Console(record=True)).build(output_dir=Path("out"))

    assert request.label == "demo"
    assert request.max_count == 2
    assert len(request.targets) == 2
    assert request.formats[0].value == "txt"
