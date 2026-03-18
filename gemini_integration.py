"""
gemini_integration.py — AFFILIFY Comment Generator
====================================================
Dual-mode Gemini integration:
  Mode A (Production): Uses google.genai SDK with GEMINI_API_KEY
  Mode B (Fallback):   Uses OpenAI-compatible endpoint with OPENAI_API_KEY
                       (supports gemini-2.5-flash via proxy)

This ensures the comment generator works in both production environments
(with a real Google AI Studio key) and in the sandbox (with OPENAI_API_KEY).
"""

import os
import asyncio
import random
import logging
from typing import Dict, Optional, List

from logger_system import log_ai, log_error, log_start, log_end, affilify_logger

logger = logging.getLogger(__name__)

# ─── Mode detection ──────────────────────────────────────────────────────────
_GEMINI_API_KEY  = os.environ.get("GEMINI_API_KEY", "").strip()
_OPENAI_API_KEY  = os.environ.get("OPENAI_API_KEY", "").strip()
_USE_NATIVE_SDK  = bool(_GEMINI_API_KEY)
_USE_OPENAI_COMPAT = (not _USE_NATIVE_SDK) and bool(_OPENAI_API_KEY)

if _USE_NATIVE_SDK:
    from google import genai
    from google.genai import types as genai_types
elif _USE_OPENAI_COMPAT:
    from openai import OpenAI as _OpenAI
    _openai_client = _OpenAI()   # OPENAI_API_KEY + base_url pre-configured by sandbox
else:
    _openai_client = None


class GeminiCommentGenerator:
    """
    Gemini 2.5 Flash powered comment generation.
    Automatically selects the available API mode on init.
    """

    MODEL_NATIVE  = "gemini-2.5-flash"
    MODEL_COMPAT  = "gemini-2.5-flash"   # same model name on OpenAI-compat endpoint

    def __init__(self, api_key: Optional[str] = None):
        # Allow explicit key override (e.g. from command_center)
        key = api_key or _GEMINI_API_KEY

        if key:
            # Native google.genai SDK
            self._mode = "native"
            self._client = genai.Client(api_key=key)
            affilify_logger.main_logger.info(
                "🧠 Gemini Comment Generator — Mode: NATIVE google.genai SDK"
            )
        elif _USE_OPENAI_COMPAT:
            # OpenAI-compatible proxy (sandbox)
            self._mode = "openai_compat"
            self._client = _openai_client
            affilify_logger.main_logger.info(
                "🧠 Gemini Comment Generator — Mode: OpenAI-compatible endpoint (gemini-2.5-flash)"
            )
        else:
            self._mode = "fallback_only"
            self._client = None
            affilify_logger.main_logger.warning(
                "⚠️  Gemini Comment Generator — No API key found. Using static fallback comments."
            )

        # AFFILIFY product knowledge injected into every prompt
        self.affilify_knowledge = (
            "AFFILIFY (affilify.eu) — AI-powered affiliate marketing platform. "
            "Generates high-converting affiliate websites in under 60 seconds. "
            "Best tool for scaling affiliate income with zero coding required."
        )

    # ─── Public API ──────────────────────────────────────────────────────────

    async def generate_comment(self, video_data: Dict, strategy: str = "STANDARD") -> str:
        """Generate a hyper-targeted comment for the given TikTok video."""
        start = log_start(
            "GenerateGeminiComment",
            video_id=video_data.get("video_id"),
            strategy=strategy,
        )

        try:
            prompt = self._build_prompt(video_data, strategy)

            if self._mode == "native":
                comment = await self._call_native(prompt)
            elif self._mode == "openai_compat":
                comment = await self._call_openai_compat(prompt)
            else:
                comment = self._get_fallback_comment(video_data)

            # Strip surrounding quotes if model added them
            comment = comment.strip().strip('"').strip("'")

            log_ai("Gemini", prompt, comment)
            log_end("GenerateGeminiComment", start, True)
            return comment

        except Exception as e:
            log_error("GeminiGeneration", str(e))
            log_end("GenerateGeminiComment", start, False, error=str(e))
            return self._get_fallback_comment(video_data)

    async def generate_batch(self, videos: List[Dict], strategy: str = "STANDARD") -> List[str]:
        """Generate comments for a batch of videos concurrently."""
        tasks = [self.generate_comment(v, strategy) for v in videos]
        return await asyncio.gather(*tasks)

    # ─── Private helpers ─────────────────────────────────────────────────────

    async def _call_native(self, prompt: str) -> str:
        """Call google.genai SDK (blocking, wrapped in thread)."""
        response = await asyncio.to_thread(
            self._client.models.generate_content,
            model=self.MODEL_NATIVE,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.9,
                top_p=0.95,
                top_k=40,
                max_output_tokens=200,
            ),
        )
        return response.text.strip()

    async def _call_openai_compat(self, prompt: str) -> str:
        """Call Gemini via OpenAI-compatible endpoint."""
        response = await asyncio.to_thread(
            self._client.chat.completions.create,
            model=self.MODEL_COMPAT,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()

    def _build_prompt(self, video_data: Dict, strategy: str) -> str:
        creator   = video_data.get("creator_username", "creator")
        desc      = video_data.get("description", "")
        hashtags  = " ".join(video_data.get("hashtags", []))
        followers = video_data.get("creator_followers", 0)

        return (
            f"You are an elite affiliate marketing expert writing TikTok comments.\n\n"
            f"Video context:\n"
            f"  Creator: @{creator} ({followers:,} followers)\n"
            f"  Description: {desc[:200]}\n"
            f"  Hashtags: {hashtags[:100]}\n"
            f"  Strategy: {strategy}\n\n"
            f"Product to promote: {self.affilify_knowledge}\n\n"
            f"Write ONE natural, human-sounding TikTok comment that:\n"
            f"  - Feels organic and relevant to the video\n"
            f"  - Subtly promotes affilify.eu\n"
            f"  - Is under 150 characters\n"
            f"  - Has NO hashtags\n"
            f"  - Does NOT start with 'I'\n\n"
            f"Reply with ONLY the comment text, nothing else."
        )

    def _get_fallback_comment(self, video_data: Dict) -> str:
        creator = video_data.get("creator_username", "")
        mention = f"@{creator} " if creator else ""
        fallbacks = [
            f"{mention}Great content! affilify.eu helped me scale my affiliate income 10x 🚀",
            "Love this strategy! affilify.eu makes building affiliate sites incredibly easy",
            f"{mention}This is exactly why I started using affilify.eu — total game changer",
            "affilify.eu - best affiliate deals! Check it out if you're serious about scaling",
            "This content is gold. affilify.eu + this strategy = unstoppable affiliate income 💯",
        ]
        return random.choice(fallbacks)
