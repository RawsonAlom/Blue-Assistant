"""Offline tests for runtime provider configuration."""

import pytest

from core import runtime
from core.brain import Brain
from integrations.openrouter_provider import OpenRouterProvider


def disable_dotenv_loading(monkeypatch):
    monkeypatch.setattr(
        runtime,
        "load_dotenv",
        lambda *_args, **_kwargs: False,
    )


def test_runtime_requires_api_key(monkeypatch):
    disable_dotenv_loading(monkeypatch)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="OPENROUTER_API_KEY"):
        runtime.create_brain()


def test_runtime_builds_brain_with_configured_model(monkeypatch):
    disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-not-real")
    monkeypatch.setenv("OPENROUTER_MODEL", "example/test-model")

    brain = runtime.create_brain()

    assert isinstance(brain, Brain)
    assert isinstance(brain._provider, OpenRouterProvider)
    assert brain._provider._model == "example/test-model"


def test_runtime_uses_free_router_by_default(monkeypatch):
    disable_dotenv_loading(monkeypatch)
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key-not-real")
    monkeypatch.delenv("OPENROUTER_MODEL", raising=False)

    brain = runtime.create_brain()

    assert brain._provider._model == "openrouter/free"
