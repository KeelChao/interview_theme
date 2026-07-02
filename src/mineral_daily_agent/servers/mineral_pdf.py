import re
import tempfile
from pathlib import Path
from typing import Any

import httpx
import pdfplumber
from mcp.server.fastmcp import FastMCP

from mineral_daily_agent.fixtures import load_fixture

mcp = FastMCP("mineral-pdf-mcp")


@mcp.tool()
def extract_resources(pdf_url: str) -> list[dict[str, Any]] | dict[str, str]:
    """Extract Indicated/Inferred resource rows from a NI 43-101 style PDF URL."""
    fixture_rows = [
        item
        for item in load_fixture("resources.json")
        if item["source_url"] == pdf_url or pdf_url.lower() in item["project"].lower()
    ]
    if fixture_rows:
        return fixture_rows

    try:
        pdf_path = _download_pdf(pdf_url)
        text = _extract_pdf_text(pdf_path)
        rows = _parse_resource_rows(text, pdf_url)
    except Exception as exc:  # noqa: BLE001 - MCP tools should return structured errors.
        return {"error": f"resource extraction failed: {exc}", "pdf_url": pdf_url}

    if not rows:
        return {
            "error": "no Indicated or Inferred resource rows found; manual review required",
            "pdf_url": pdf_url,
        }
    return rows


def _download_pdf(pdf_url: str) -> Path:
    response = httpx.get(pdf_url, timeout=20.0, follow_redirects=True)
    response.raise_for_status()
    content_type = response.headers.get("content-type", "").lower()
    if "pdf" not in content_type and not pdf_url.endswith(".pdf"):
        raise ValueError("URL did not look like a PDF")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as handle:
        handle.write(response.content)
        return Path(handle.name)


def _extract_pdf_text(pdf_path: Path) -> str:
    parts: list[str] = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            parts.append(page.extract_text() or "")
    return "\n".join(parts)


def _parse_resource_rows(text: str, pdf_url: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    pattern = re.compile(
        r"(?P<category>Indicated|Inferred)\s+"
        r"(?P<ore>\d+(?:\.\d+)?)\s*(?:Mt|million tonnes).*?"
        r"(?P<grade>\d+(?:\.\d+)?\s*(?:g/t\s*Au|%\s*Cu|%\s*Li2O)).*?"
        r"(?P<metal>\d+(?:\.\d+)?\s*(?:Moz|koz|t|Mt).*?)",
        re.IGNORECASE | re.DOTALL,
    )
    for match in pattern.finditer(text):
        rows.append(
            {
                "project": "Unknown project",
                "company": "Unknown company",
                "category": match.group("category").title(),
                "ore_mt": float(match.group("ore")),
                "grade": " ".join(match.group("grade").split()),
                "metal": " ".join(match.group("metal").split()[:4]),
                "source_url": pdf_url,
                "source_title": "Live PDF extraction",
            }
        )
    return rows


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
