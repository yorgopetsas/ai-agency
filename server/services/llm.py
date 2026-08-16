"""
LLM Router Service
=================
Multi-provider LLM client with round-robin rotation and local-first fallback.

Providers:
- ollama: local or remote Ollama server (free, no key)
- openai_compatible: OpenAI, Groq, OpenRouter, Together, etc. (OpenAI chat API)
- gemini: Google AI Studio (generous free tier)

Strategy:
- Per-article rotation: automation picks one provider per article, so
  research + write use the same model for consistency.
- Local-first fallback: when enabled, Ollama (local, then server) is tried
  first, then hosted providers in round-robin order. Any provider that
  fails is skipped and the next one in the chain is tried.

Usage:
    result = llm_client.generate(prompt, system=..., max_tokens=800, temperature=0.7)
    text, provider = result["text"], result["provider"]

    provider_name = llm_client.pick()          # choose a provider for an article
    result = llm_client.generate(..., preferred=provider_name)
"""

import json
import os
import time
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BaseProvider:
    """Common provider interface."""

    def __init__(self, config: Dict):
        self.name = config["name"]
        self.type = config["type"]
        self.model = config.get("model", "")
        self.enabled = config.get("enabled", True)
        self.weight = config.get("weight", 1.0)
        self.config = config

    def available(self) -> bool:
        """Whether the provider is usable right now."""
        raise NotImplementedError

    def generate(self, prompt: str, system: Optional[str] = None,
                 max_tokens: int = 800, temperature: float = 0.7) -> str:
        """Generate text. Raises on failure."""
        raise NotImplementedError

    def __repr__(self):
        return f"<{self.type} {self.name} ({self.model})>"


class OllamaProvider(BaseProvider):
    """Local or remote Ollama server (free, no API key)."""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = config["base_url"].rstrip("/")

    def available(self) -> bool:
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return resp.status_code == 200
        except Exception:
            return False

    def generate(self, prompt, system=None, max_tokens=800, temperature=0.7) -> str:
        data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        if system:
            data["system"] = system

        resp = requests.post(f"{self.base_url}/api/generate", json=data, timeout=180)
        resp.raise_for_status()
        text = resp.json().get("response", "").strip()
        if not text:
            raise RuntimeError("Ollama returned empty response")
        return text


class OpenAICompatibleProvider(BaseProvider):
    """OpenAI, Groq, OpenRouter, Together, etc. — all use the chat API."""

    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = config["base_url"].rstrip("/")
        self.api_key = os.environ.get(config.get("api_key_env", ""), "")

    def available(self) -> bool:
        if not self.api_key:
            return False
        # Light ping to validate key (cached by the router)
        try:
            resp = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=8
            )
            return resp.status_code == 200
        except Exception:
            return False

    def generate(self, prompt, system=None, max_tokens=800, temperature=0.7) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        resp = requests.post(
            f"{self.base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json=payload,
            timeout=180
        )
        resp.raise_for_status()
        data = resp.json()
        text = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
        if not text:
            raise RuntimeError("Provider returned empty response")
        return text


class GeminiProvider(BaseProvider):
    """Google Gemini via the AI Studio REST API (generous free tier)."""

    API_BASE = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = os.environ.get(config.get("api_key_env", ""), "")

    def available(self) -> bool:
        return bool(self.api_key)

    def generate(self, prompt, system=None, max_tokens=800, temperature=0.7) -> str:
        payload = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }
        if system:
            payload["systemInstruction"] = {"parts": [{"text": system}]}

        url = f"{self.API_BASE}/models/{self.model}:generateContent?key={self.api_key}"
        resp = requests.post(url, json=payload, timeout=180)
        resp.raise_for_status()
        data = resp.json()
        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except (KeyError, IndexError):
            raise RuntimeError(f"Gemini unexpected response: {data}")
        if not text:
            raise RuntimeError("Gemini returned empty response")
        return text


PROVIDER_TYPES = {
    "ollama": OllamaProvider,
    "openai_compatible": OpenAICompatibleProvider,
    "gemini": GeminiProvider,
}


class LLMRouter:
    """
    Rotates across available providers and falls back on failure.
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or (Path(__file__).parent.parent / "config" / "llm_config.json")
        self.config = self._load_config()
        self.providers = self._build_providers()
        self._availability_cache: Dict[str, tuple] = {}
        self._rr_index = 0
        self._rr_counts = {}

    # --- Setup helpers ---

    def _load_config(self) -> Dict:
        if self.config_path.exists():
            return json.loads(self.config_path.read_text())
        return {}

    def _build_providers(self) -> List[BaseProvider]:
        providers = []
        for spec in self.config.get("providers", []):
            cls = PROVIDER_TYPES.get(spec.get("type"))
            if not cls:
                logger.warning(f"Unknown provider type: {spec.get('type')}")
                continue
            try:
                providers.append(cls(spec))
            except Exception as e:
                logger.warning(f"Failed to build provider {spec.get('name')}: {e}")
        return providers

    # --- Availability ---

    def is_available(self, provider: BaseProvider) -> bool:
        """Availability with a short cache to avoid hammering health checks."""
        cache_ttl = self.config.get("availability_cache_seconds", 60)
        cached = self._availability_cache.get(provider.name)
        now = time.time()
        if cached and now - cached[0] < cache_ttl:
            return cached[1]

        try:
            ok = provider.enabled and provider.available()
        except Exception:
            ok = False
        self._availability_cache[provider.name] = (now, ok)
        return ok

    def available_providers(self) -> List[BaseProvider]:
        return [p for p in self.providers if self.is_available(p)]

    # --- Selection ---

    def pick(self, preferred: Optional[str] = None) -> Optional[str]:
        """
        Choose a provider for the next article (round-robin over available).

        Args:
            preferred: If given and available, use this provider instead.

        Returns:
            Provider name or None if nothing is available.
        """
        available = self.available_providers()
        if not available:
            return None

        if preferred:
            for p in available:
                if p.name == preferred:
                    return p.name

        # Weighted round-robin (smooth): track counts, pick highest weight/count ratio
        if self.config.get("strategy", "round_robin") == "round_robin":
            best = None
            best_ratio = -1.0
            for p in available:
                count = self._rr_counts.get(p.name, 0)
                ratio = p.weight / (count + 1)
                if ratio > best_ratio:
                    best_ratio = ratio
                    best = p
            self._rr_counts[best.name] = self._rr_counts.get(best.name, 0) + 1
            return best.name

        # fallback: simple round-robin by index
        idx = self._rr_index % len(available)
        self._rr_index += 1
        return available[idx].name

    def _ordered_candidates(self, preferred: Optional[str] = None) -> List[BaseProvider]:
        """
        Candidate order for a generate call.
        - preferred provider first if available
        - local-first: ollama providers (local then server) before hosted ones
        - then remaining available providers
        """
        available = self.available_providers()
        if not available:
            return []

        preferred_p = next((p for p in available if p.name == preferred), None)
        ordered = [preferred_p] if preferred_p else []

        if self.config.get("fallback_first", True):
            ollamas = [p for p in available if p.type == "ollama"]
            for ollama in ollamas:
                if ollama not in ordered:
                    ordered.append(ollama)

        rest = [p for p in available if p not in ordered]
        ordered.extend(rest)
        return ordered

    # --- Generation ---

    def generate(self, prompt: str, system: Optional[str] = None,
                 max_tokens: int = 800, temperature: float = 0.7,
                 preferred: Optional[str] = None) -> Dict:
        """
        Generate text, trying candidates in order with fallback.

        Returns:
            {"success": bool, "text": str, "provider": str, "model": str,
             "tried": [provider names], "error": str}
        """
        candidates = self._ordered_candidates(preferred)
        if not candidates:
            return {
                "success": False,
                "text": "",
                "provider": None,
                "model": None,
                "tried": [],
                "error": "No LLM providers available (check Ollama, API keys)"
            }

        tried = []
        errors = []
        for provider in candidates:
            tried.append(provider.name)
            try:
                logger.info(f"LLM generate via {provider.name} ({provider.model})")
                text = provider.generate(prompt, system=system,
                                         max_tokens=max_tokens,
                                         temperature=temperature)
                return {
                    "success": True,
                    "text": text,
                    "provider": provider.name,
                    "model": provider.model,
                    "tried": tried,
                    "error": ""
                }
            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                errors.append(f"{provider.name}: {e}")
                # If this provider was selected by rotation but now failing,
                # invalidate the availability cache so it's skipped next time.
                self._availability_cache.pop(provider.name, None)

        return {
            "success": False,
            "text": "",
            "provider": None,
            "model": None,
            "tried": tried,
            "error": " | ".join(errors)
        }

    # --- Status ---

    def get_status(self) -> List[Dict]:
        """Provider status for the admin panel."""
        statuses = []
        for p in self.providers:
            statuses.append({
                "name": p.name,
                "type": p.type,
                "model": p.model,
                "enabled": p.enabled,
                "available": self.is_available(p)
            })
        return statuses


# Default instance
llm_client = LLMRouter()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("LLM Router - Provider status")
    for s in llm_client.get_status():
        print(f"  {'OK ' if s['available'] else 'DOWN'} {s['name']:>15}  {s['type']:<18} {s['model']}")

    print("\nTesting rotation (3 picks):")
    for i in range(3):
        p = llm_client.pick()
        print(f"  pick {i + 1}: {p}")

    print("\nTesting generation (fallback chain):")
    result = llm_client.generate("Reply with exactly: LLM router works",
                                 max_tokens=50, temperature=0.2)
    print(f"  success={result['success']} provider={result['provider']} model={result['model']}")
    print(f"  tried={result['tried']}")
    if result["success"]:
        print(f"  text={result['text'][:80]!r}")
