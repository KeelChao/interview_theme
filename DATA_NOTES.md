# Data Notes

The repository includes fixture data to make the interview demo reproducible.
Fixtures are not presented as live market data.

## `data/fixtures/news.json`

- Primary key: `url`.
- Fields: `title`, `published_at`, `source`, `url`, `summary`, `tags`.
- Used by `mining-news-mcp.search` and `mining-news-mcp.fetch_article`.
- Deduplication strategy: URL is canonical; same URL means same article.

## `data/fixtures/resources.json`

- Logical key: `project + company + category + source_url`.
- Fields: `project`, `company`, `category`, `ore_mt`, `grade`, `metal`,
  `source_url`, `source_title`.
- Used by `mineral-pdf-mcp.extract_resources`.
- Categories are constrained to `Indicated` and `Inferred`.

## `data/fixtures/prices.json`

- Logical key: `commodity + date + source`.
- Fields: `commodity`, `date`, `price`, `unit`, `source`, `source_url`.
- Used by `lme-price-mcp.get_price` and `lme-price-mcp.get_trend`.

## Why Fixture First

The original task mentions news crawling, official policy pages, LME/SHFE style
price data, and NI 43-101 PDF extraction. Those sources are useful enhancement
targets, but they are risky for a 5-minute interview run because of login walls,
rate limits, anti-crawling, and PDF format variance. This project keeps the
MCP interfaces stable while making the default demo deterministic.
