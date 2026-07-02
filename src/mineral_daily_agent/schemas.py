from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class Citation(BaseModel):
    title: str
    url: HttpUrl
    source: str


class NewsItem(BaseModel):
    title: str
    published_at: str
    source: str
    url: HttpUrl
    summary: str
    tags: list[str] = Field(default_factory=list)


class ResourceEstimate(BaseModel):
    project: str
    company: str
    category: Literal["Indicated", "Inferred"]
    ore_mt: float
    grade: str
    metal: str
    source_url: HttpUrl
    source_title: str


class PricePoint(BaseModel):
    commodity: str
    date: str
    price: float
    unit: str
    source: str
    source_url: HttpUrl


class PriceTrend(BaseModel):
    commodity: str
    days: int
    start_date: str
    end_date: str
    start_price: float
    end_price: float
    change_pct: float
    unit: str
    source: str
    source_url: HttpUrl


class EvidenceBundle(BaseModel):
    query: str
    topic: str
    days: int
    news: list[NewsItem]
    resources: list[ResourceEstimate]
    prices: list[PriceTrend]
    warnings: list[str] = Field(default_factory=list)


class BriefingResult(BaseModel):
    markdown: str
    evidence: EvidenceBundle
