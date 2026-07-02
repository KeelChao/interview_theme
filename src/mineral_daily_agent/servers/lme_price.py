from datetime import date
from typing import Any

from mcp.server.fastmcp import FastMCP

from mineral_daily_agent.fixtures import load_fixture

mcp = FastMCP("lme-price-mcp")


@mcp.tool()
def get_price(commodity: str, date_value: str | None = None) -> dict[str, Any]:
    """Get one commodity price point by commodity and optional date."""
    rows = _commodity_rows(commodity)
    if not rows:
        return {"error": f"unsupported commodity: {commodity}"}
    if date_value:
        for row in rows:
            if row["date"] == date_value:
                return row
    return sorted(rows, key=lambda row: row["date"])[-1]


@mcp.tool()
def get_trend(commodity: str, days: int = 7) -> dict[str, Any]:
    """Get a simple price trend over the latest fixture window."""
    rows = sorted(_commodity_rows(commodity), key=lambda row: row["date"])
    if len(rows) < 2:
        return {"error": f"not enough price points for {commodity}"}

    start = rows[0]
    end = rows[-1]
    change_pct = round(((end["price"] - start["price"]) / start["price"]) * 100, 2)
    return {
        "commodity": commodity.lower(),
        "days": days,
        "start_date": start["date"],
        "end_date": end["date"],
        "start_price": start["price"],
        "end_price": end["price"],
        "change_pct": change_pct,
        "unit": end["unit"],
        "source": end["source"],
        "source_url": end["source_url"],
        "as_of": str(date.today()),
    }


def _commodity_rows(commodity: str) -> list[dict[str, Any]]:
    normalized = commodity.lower().strip()
    return [row for row in load_fixture("prices.json") if row["commodity"].lower() == normalized]


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
