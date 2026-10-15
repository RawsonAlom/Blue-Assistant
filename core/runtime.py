"""Runtime construction for BLUE's OpenRouter-backed Brain."""

import os
from pathlib import Path

from dotenv import load_dotenv

from core.brain import Brain
from integrations.openrouter_provider import OpenRouterProvider

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL = "openrouter/free"


def create_brain() -> Brain:
    """Load local configuration and construct the runtime Brain."""

    load_dotenv(PROJECT_ROOT / ".env", override=False)

    api_key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "OPENROUTER_API_KEY is missing. "
            "Add it to the project .env file."
        )

    model = os.environ.get("OPENROUTER_MODEL", DEFAULT_MODEL).strip()
    if not model:
        raise RuntimeError("OPENROUTER_MODEL must not be empty.")

    provider = OpenRouterProvider(api_key=api_key, model=model)
    return Brain(provider)
