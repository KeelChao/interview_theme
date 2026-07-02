import argparse
import asyncio
import sys

from dotenv import load_dotenv
from rich.console import Console

from mineral_daily_agent.agent import MineralDailyAgent
from mineral_daily_agent.config import get_settings
from mineral_daily_agent.llm import DeepSeekBriefingLLM
from mineral_daily_agent.mcp_client import MCPToolClient


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a mineral rights daily briefing.")
    parser.add_argument(
        "query",
        nargs="?",
        default="给我生成一份关于 Pilbara 锂矿的今日简报",
        help="Natural-language briefing request.",
    )
    parser.add_argument("--days", type=int, default=None, help="Lookback window for news/prices.")
    args = parser.parse_args()

    load_dotenv()
    settings = get_settings()
    days = args.days or settings.briefing_default_days
    console = Console()

    try:
        result = asyncio.run(
            MineralDailyAgent(
                mcp_client=MCPToolClient(),
                llm=DeepSeekBriefingLLM(settings),
            ).run(args.query, days=days)
        )
    except RuntimeError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        sys.exit(1)
    console.print(result.markdown)


if __name__ == "__main__":
    main()
