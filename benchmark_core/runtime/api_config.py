from __future__ import annotations

import os
from dataclasses import asdict, dataclass


@dataclass
class APISettings:
    provider: str = "openai"
    model: str = "gpt-4.1-mini"
    api_base: str = "https://api.openai.com/v1"
    api_endpoint: str = "/chat/completions"
    api_key: str = ""
    timeout_sec: int = 60
    temperature: float = 0.0
    max_tokens: int = 512

    def validate(self) -> list[str]:
        issues = []
        if self.provider not in {"openai", "openrouter", "anthropic"}:
            issues.append("provider must be openai/openrouter/anthropic")
        if not self.api_key:
            issues.append(f"missing API key for provider={self.provider}")
        if not self.api_endpoint.startswith("/"):
            issues.append("api_endpoint must start with '/'")
        return issues

    def public_dict(self) -> dict:
        payload = asdict(self)
        payload["api_key"] = "***" if self.api_key else ""
        return payload


def load_api_settings(cfg: dict | None = None) -> APISettings:
    cfg = cfg or {}
    provider = str(cfg.get("provider") or os.getenv("CLAWDOJO_API_PROVIDER", "openai")).lower()
    key = str(cfg.get("api_key") or os.getenv("CLAWDOJO_API_KEY", "") or os.getenv(_key_env(provider), ""))
    return APISettings(
        provider=provider,
        model=str(cfg.get("model") or os.getenv("CLAWDOJO_MODEL", "gpt-4.1-mini")),
        api_base=str(cfg.get("api_base") or os.getenv("CLAWDOJO_API_BASE", _default_base(provider))),
        api_endpoint=str(cfg.get("api_endpoint") or os.getenv("CLAWDOJO_API_ENDPOINT", "/chat/completions")),
        api_key=key,
        timeout_sec=int(cfg.get("timeout_sec", os.getenv("CLAWDOJO_TIMEOUT_SEC", 60))),
        max_tokens=int(cfg.get("max_tokens", 512)),
    )


def _default_base(provider: str) -> str:
    if provider == "anthropic":
        return "https://api.anthropic.com"
    if provider == "openrouter":
        return "https://openrouter.ai/api/v1"
    return "https://api.openai.com/v1"


def _key_env(provider: str) -> str:
    return {"anthropic": "ANTHROPIC_API_KEY", "openrouter": "OPENROUTER_API_KEY"}.get(provider, "OPENAI_API_KEY")
