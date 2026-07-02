import json
from typing import Protocol

import httpx
from openai import OpenAI

from mineral_daily_agent.config import Settings
from mineral_daily_agent.schemas import EvidenceBundle


class BriefingLLM(Protocol):
    def generate(self, evidence: EvidenceBundle) -> str:
        """Generate a Markdown briefing from structured evidence."""


class DeepSeekBriefingLLM:
    def __init__(self, settings: Settings) -> None:
        if not settings.deepseek_api_key:
            raise RuntimeError(
                "DEEPSEEK_API_KEY is required. Copy .env.example to .env and set your key."
            )
        self._model = settings.deepseek_model
        self._client = OpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url,
            http_client=httpx.Client(trust_env=settings.deepseek_trust_env),
        )

    def generate(self, evidence: EvidenceBundle) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a mining analyst agent. Produce concise Chinese Markdown. "
                        "Use only the supplied evidence. If evidence is missing or tool output "
                        "contains an error, say so explicitly and do not invent facts. Include "
                        "source links in the final references section. Do not use emoji."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Generate a mineral rights daily briefing from this JSON evidence:\n"
                        + json.dumps(evidence.model_dump(mode="json"), ensure_ascii=False, indent=2)
                    ),
                },
            ],
            temperature=0.2,
        )
        content = response.choices[0].message.content
        if not content:
            raise RuntimeError("DeepSeek returned an empty briefing")
        return content
