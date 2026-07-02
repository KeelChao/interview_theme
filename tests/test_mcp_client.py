import pytest

from mineral_daily_agent.mcp_client import MCPToolClient


@pytest.mark.asyncio
async def test_mcp_client_calls_price_server_over_stdio() -> None:
    result = await MCPToolClient().call("price", "get_trend", {"commodity": "lithium", "days": 7})

    assert result["commodity"] == "lithium"
    assert result["change_pct"] == 3.9
