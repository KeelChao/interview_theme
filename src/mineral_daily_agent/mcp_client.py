import json
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@dataclass(frozen=True)
class ServerSpec:
    name: str
    module: str


SERVER_SPECS: dict[str, ServerSpec] = {
    "news": ServerSpec("mining-news-mcp", "mineral_daily_agent.servers.mining_news"),
    "pdf": ServerSpec("mineral-pdf-mcp", "mineral_daily_agent.servers.mineral_pdf"),
    "price": ServerSpec("lme-price-mcp", "mineral_daily_agent.servers.lme_price"),
}


class MCPToolClient:
    async def call(self, server_key: str, tool_name: str, arguments: Mapping[str, Any]) -> Any:
        spec = SERVER_SPECS[server_key]
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", spec.module],
        )
        async with (
            stdio_client(params) as (read_stream, write_stream),
            ClientSession(read_stream, write_stream) as session,
        ):
            await session.initialize()
            result = await session.call_tool(tool_name, arguments=dict(arguments))
            return _decode_tool_result(result)


def _decode_tool_result(result: Any) -> Any:
    structured = getattr(result, "structuredContent", None) or getattr(
        result, "structured_content", None
    )
    if structured is not None:
        if isinstance(structured, dict) and "result" in structured:
            return structured["result"]
        return structured

    content = getattr(result, "content", [])
    if not content:
        return None
    text = getattr(content[0], "text", str(content[0]))
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text
