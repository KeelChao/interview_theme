import pytest

from mineral_daily_agent.agent import MineralDailyAgent
from mineral_daily_agent.schemas import EvidenceBundle


class FakeMCPClient:
    async def call(self, server_key: str, tool_name: str, arguments: dict[str, object]) -> object:
        if server_key == "news":
            return [
                {
                    "title": "Pilbara fixture news",
                    "published_at": "2026-07-01",
                    "source": "fixture",
                    "url": "https://example.com/news",
                    "summary": "Stable shipments.",
                    "tags": ["pilbara", "lithium"],
                }
            ]
        if server_key == "pdf":
            return [
                {
                    "project": "Pilgangoora",
                    "company": "Pilbara Minerals",
                    "category": "Indicated",
                    "ore_mt": 214.0,
                    "grade": "1.17% Li2O",
                    "metal": "2.50 Mt Li2O contained",
                    "source_url": "https://example.com/resource.pdf",
                    "source_title": "fixture resource",
                }
            ]
        if server_key == "price":
            return {
                "commodity": "lithium",
                "days": 7,
                "start_date": "2026-06-25",
                "end_date": "2026-07-01",
                "start_price": 8200,
                "end_price": 8520,
                "change_pct": 3.9,
                "unit": "USD/t",
                "source": "fixture",
                "source_url": "https://example.com/price",
            }
        raise AssertionError(f"unexpected call: {server_key}.{tool_name}")


class FakeLLM:
    def generate(self, evidence: EvidenceBundle) -> str:
        assert evidence.topic == "Pilbara lithium"
        assert evidence.news
        assert evidence.resources
        assert evidence.prices
        return "# Pilbara lithium briefing\n\n## References\n- https://example.com/news"


@pytest.mark.asyncio
async def test_agent_builds_evidence_and_markdown() -> None:
    result = await MineralDailyAgent(FakeMCPClient(), FakeLLM()).run(
        "给我生成一份关于 Pilbara 锂矿的今日简报"
    )

    assert "Pilbara lithium briefing" in result.markdown
    assert result.evidence.topic == "Pilbara lithium"
    assert result.evidence.prices[0].change_pct == 3.9
