"""
ai_handler.py - AI Logic Layer for mousum-graphics-mvp
========================================================

Encapsulates all communication with AI providers (Anthropic Claude,
OpenAI, or a local LLM such as Ollama) and contains the logic for
turning a raw design prompt from the React frontend into a structured
design concept (color palette, typography, layout notes, mood, etc.).

Keeping this separate from main.py means the FastAPI routes stay thin —
they just receive a request, hand it to AIHandler, and return the result.

Usage from main.py:

    from ai_handler import AIHandler

    handler = AIHandler()  # reads provider/config from environment

    result = handler.generate_design_concept(
        prompt="A minimalist logo for a coffee brand called 'Solstice'",
        style="minimalist",
    )
"""

import os
import json
import logging
from enum import Enum
from typing import Optional, Dict, Any, List

import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("mousum-graphics-mvp.ai_handler")
logging.basicConfig(level=logging.INFO)


# ---------------------------------------------------------------------------
# Provider configuration
# ---------------------------------------------------------------------------

class AIProvider(str, Enum):
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    LOCAL = "local"  # e.g. Ollama running at http://localhost:11434


class AIHandlerError(Exception):
    """Raised when the AI backend fails to produce a usable response."""


# ---------------------------------------------------------------------------
# Prompt template for design requests
# ---------------------------------------------------------------------------

DESIGN_SYSTEM_PROMPT = """You are a senior graphic design assistant embedded in a \
design tool. Given a user's design brief, respond with a single JSON object \
(no markdown fences, no commentary) with exactly these fields:

{
  "concept_summary": "1-2 sentence description of the overall design idea",
  "color_palette": [
    {"name": "string", "hex": "#RRGGBB"}
  ],
  "typography": {
    "heading_font": "string (a real, commonly available font name)",
    "body_font": "string (a real, commonly available font name)"
  },
  "layout_notes": ["short bullet points describing composition/layout"],
  "mood_keywords": ["3-6 single or two-word descriptors"]
}

Tailor the palette size (3-6 colors) and layout notes (2-5 bullets) to the \
complexity of the brief. Only return the JSON object, nothing else."""


class AIHandler:
    """
    Provider-agnostic handler for AI design requests.

    Reads configuration from environment variables so the same code works
    across Anthropic, OpenAI, and local LLMs without code changes:

        AI_PROVIDER=anthropic|openai|local   (default: anthropic)
        ANTHROPIC_API_KEY=...
        ANTHROPIC_MODEL=claude-sonnet-4-6    (default)
        OPENAI_API_KEY=...
        OPENAI_MODEL=gpt-4o-mini             (default)
        LOCAL_LLM_URL=http://localhost:11434 (default, Ollama-style)
        LOCAL_LLM_MODEL=llama3               (default)
    """

    def __init__(self, provider: Optional[str] = None):
        self.provider = AIProvider(provider or os.getenv("AI_PROVIDER", "anthropic"))

        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        self.anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")

        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        self.local_llm_url = os.getenv("LOCAL_LLM_URL", "http://localhost:11434")
        self.local_llm_model = os.getenv("LOCAL_LLM_MODEL", "llama3")

        self._client = None
        self._init_client()

    # -----------------------------------------------------------------
    # Client setup
    # -----------------------------------------------------------------

    def _init_client(self) -> None:
        if self.provider == AIProvider.ANTHROPIC:
            if not self.anthropic_api_key:
                logger.warning("ANTHROPIC_API_KEY not set — Anthropic calls will fail.")
                return
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.anthropic_api_key)

        elif self.provider == AIProvider.OPENAI:
            if not self.openai_api_key:
                logger.warning("OPENAI_API_KEY not set — OpenAI calls will fail.")
                return
            import openai
            self._client = openai.OpenAI(api_key=self.openai_api_key)

        elif self.provider == AIProvider.LOCAL:
            # No persistent client needed — we call the REST API directly.
            self._client = "local"

    def is_configured(self) -> bool:
        return self._client is not None

    # -----------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------

    def generate_design_concept(
        self,
        prompt: str,
        style: Optional[str] = None,
        palette_preference: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.8,
    ) -> Dict[str, Any]:
        """
        Turn a raw design brief into a structured design concept.

        Args:
            prompt: The user's design request, e.g. "A logo for a coffee brand".
            style: Optional style hint, e.g. "minimalist", "retro", "corporate".
            palette_preference: Optional color hint, e.g. "warm earth tones".
            max_tokens: Cap on response length.
            temperature: Creativity level (0.0-1.0).

        Returns:
            A dict matching the DESIGN_SYSTEM_PROMPT schema.

        Raises:
            AIHandlerError: if the provider isn't configured, the call fails,
                             or the response can't be parsed as valid JSON.
        """
        if not self.is_configured():
            raise AIHandlerError(
                f"AI provider '{self.provider.value}' is not configured. "
                f"Check your environment variables."
            )

        user_prompt = self._build_user_prompt(prompt, style, palette_preference)

        raw_text = self._call_provider(
            system=DESIGN_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
        )

        return self._parse_design_response(raw_text)

    def generate_raw(
        self,
        prompt: str,
        system: Optional[str] = None,
        history: Optional[List[Dict[str, str]]] = None,
        max_tokens: int = 1024,
        temperature: float = 1.0,
    ) -> str:
        """
        Free-form passthrough for non-design prompts (general chat, etc.),
        returned as plain text rather than parsed JSON.
        """
        if not self.is_configured():
            raise AIHandlerError(
                f"AI provider '{self.provider.value}' is not configured."
            )
        return self._call_provider(
            system=system,
            user_prompt=prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            history=history,
        )

    # -----------------------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------------------

    @staticmethod
    def _build_user_prompt(
        prompt: str, style: Optional[str], palette_preference: Optional[str]
    ) -> str:
        parts = [f"Design brief: {prompt}"]
        if style:
            parts.append(f"Preferred style: {style}")
        if palette_preference:
            parts.append(f"Palette preference: {palette_preference}")
        return "\n".join(parts)

    def _call_provider(
        self,
        user_prompt: str,
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.8,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> str:
        try:
            if self.provider == AIProvider.ANTHROPIC:
                return self._call_anthropic(user_prompt, system, max_tokens, temperature, history)
            elif self.provider == AIProvider.OPENAI:
                return self._call_openai(user_prompt, system, max_tokens, temperature, history)
            elif self.provider == AIProvider.LOCAL:
                return self._call_local(user_prompt, system, max_tokens, temperature, history)
        except AIHandlerError:
            raise
        except Exception as e:
            logger.exception(f"AI provider call failed ({self.provider.value})")
            raise AIHandlerError(f"AI provider call failed: {e}") from e

        raise AIHandlerError(f"Unsupported provider: {self.provider}")

    def _call_anthropic(self, user_prompt, system, max_tokens, temperature, history):
        messages = list(history) if history else []
        messages.append({"role": "user", "content": user_prompt})

        kwargs = {
            "model": self.anthropic_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        }
        if system:
            kwargs["system"] = system

        completion = self._client.messages.create(**kwargs)
        return "".join(block.text for block in completion.content if block.type == "text")

    def _call_openai(self, user_prompt, system, max_tokens, temperature, history):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_prompt})

        completion = self._client.chat.completions.create(
            model=self.openai_model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        return completion.choices[0].message.content

    def _call_local(self, user_prompt, system, max_tokens, temperature, history):
        """
        Calls a local LLM server using an Ollama-compatible /api/chat endpoint.
        Swap this out if you're using a different local server (LM Studio,
        llama.cpp server, vLLM, etc.) — the response parsing will differ.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_prompt})

        try:
            resp = requests.post(
                f"{self.local_llm_url}/api/chat",
                json={
                    "model": self.local_llm_model,
                    "messages": messages,
                    "stream": False,
                    "options": {"temperature": temperature},
                },
                timeout=120,
            )
            resp.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise AIHandlerError(f"Could not reach local LLM at {self.local_llm_url}: {e}") from e

        data = resp.json()
        return data.get("message", {}).get("content", "")

    @staticmethod
    def _parse_design_response(raw_text: str) -> Dict[str, Any]:
        """
        Parses the model's JSON output into a dict, tolerating minor
        formatting slip-ups like stray markdown code fences.
        """
        cleaned = raw_text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.lower().startswith("json"):
                cleaned = cleaned[4:]
            cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {raw_text[:500]}")
            raise AIHandlerError(
                "The AI response could not be parsed as valid design JSON."
            ) from e
