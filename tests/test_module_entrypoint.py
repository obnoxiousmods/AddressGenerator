from __future__ import annotations

import runpy

import pytest


def test_module_entrypoint_calls_main(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"value": False}

    def fake_main() -> None:
        called["value"] = True

    monkeypatch.setattr("address_generator.cli.main", fake_main)
    runpy.run_module("address_generator", run_name="__main__")

    assert called["value"] is True
