"""Minimal application settings loaded from environment variables."""

import os
from dataclasses import dataclass

_ALLOWED_ENVIRONMENTS = {"development", "test", "production"}
_ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated, non-secret application settings."""

    app_name: str = "BLUE"
    environment: str = "development"
    log_level: str = "INFO"

    def __post_init__(self) -> None:
        if not self.app_name.strip():
            raise ValueError("Application name must not be empty.")

        if self.environment not in _ALLOWED_ENVIRONMENTS:
            raise ValueError(
                f"Unsupported environment: {self.environment!r}"
            )

        if self.log_level not in _ALLOWED_LOG_LEVELS:
            raise ValueError(f"Unsupported log level: {self.log_level!r}")

    @classmethod
    def from_environment(cls) -> Settings:
        """Load and validate settings without reading secret credentials."""

        return cls(
            app_name=os.environ.get("BLUE_APP_NAME", "BLUE").strip(),
            environment=os.environ.get(
                "BLUE_ENV", "development"
            ).strip().lower(),
            log_level=os.environ.get(
                "BLUE_LOG_LEVEL", "INFO"
            ).strip().upper(),
        )
