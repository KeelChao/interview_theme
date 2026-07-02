from typing import Any

from mineral_daily_agent.llm import BriefingLLM
from mineral_daily_agent.mcp_client import MCPToolClient
from mineral_daily_agent.schemas import (
    BriefingResult,
    EvidenceBundle,
    NewsItem,
    PriceTrend,
    ResourceEstimate,
)

PILBARA_RESOURCE_URL = "https://www.pilbaraminerals.com.au/fixture/pilgangoora-resources.pdf"


class MineralDailyAgent:
    def __init__(self, mcp_client: MCPToolClient, llm: BriefingLLM) -> None:
        self._mcp_client = mcp_client
        self._llm = llm

    async def run(self, query: str, days: int = 7) -> BriefingResult:
        topic = _infer_topic(query)
        warnings: list[str] = []

        news_raw = await self._safe_call(
            "news", "search", {"query": f"{topic} lithium policy price", "days": days}, warnings
        )
        resources_raw = await self._safe_call(
            "pdf", "extract_resources", {"pdf_url": PILBARA_RESOURCE_URL}, warnings
        )
        prices_raw = await self._safe_call(
            "price", "get_trend", {"commodity": "lithium", "days": days}, warnings
        )

        evidence = EvidenceBundle(
            query=query,
            topic=topic,
            days=days,
            news=[NewsItem.model_validate(item) for item in _as_list(news_raw)],
            resources=[ResourceEstimate.model_validate(item) for item in _as_list(resources_raw)],
            prices=[PriceTrend.model_validate(item) for item in _as_list(prices_raw)],
            warnings=warnings,
        )
        markdown = self._llm.generate(evidence)
        return BriefingResult(markdown=markdown, evidence=evidence)

    async def _safe_call(
        self,
        server_key: str,
        tool_name: str,
        arguments: dict[str, Any],
        warnings: list[str],
    ) -> Any:
        try:
            result = await self._mcp_client.call(server_key, tool_name, arguments)
        except Exception as exc:  # noqa: BLE001 - preserve agent continuity for demos.
            warnings.append(f"{server_key}.{tool_name} failed: {exc}")
            return []

        if isinstance(result, dict) and "error" in result:
            warnings.append(f"{server_key}.{tool_name}: {result['error']}")
            return []
        return result


def _infer_topic(query: str) -> str:
    lowered = query.lower()
    if "pilbara" in lowered or "pilgangoora" in lowered:
        return "Pilbara lithium"
    return query.strip() or "mineral rights"


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]
