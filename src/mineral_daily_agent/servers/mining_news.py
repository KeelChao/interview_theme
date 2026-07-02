from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

from mineral_daily_agent.fixtures import load_fixture, match_text

mcp = FastMCP("mining-news-mcp")


@mcp.tool()
def search(query: str, days: int = 7) -> list[dict[str, Any]]:
    """Search recent mining news articles from fixture-first sources."""
    items = load_fixture("news.json")
    matched = [item for item in items if match_text(item, query)]
    return matched[:10] if matched else items[:5]


@mcp.tool()
def fetch_article(url: str) -> dict[str, Any]:
    """Fetch one article by URL, falling back to a lightweight live HTTP fetch."""
    for item in load_fixture("news.json"):
        if item["url"] == url:
            return {
                **item,
                "body": item["summary"],
                "retrieval_mode": "fixture",
            }

    try:
        response = httpx.get(url, timeout=8.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        return {"url": url, "error": f"failed to fetch article: {exc}"}

    text = " ".join(response.text.split())
    return {
        "url": url,
        "body": text[:4000],
        "retrieval_mode": "live_http",
    }


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
