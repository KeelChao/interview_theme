from mineral_daily_agent.fixtures import load_fixture
from mineral_daily_agent.schemas import NewsItem, PricePoint, ResourceEstimate


def test_fixture_schemas_are_valid() -> None:
    for item in load_fixture("news.json"):
        NewsItem.model_validate(item)
    for item in load_fixture("resources.json"):
        ResourceEstimate.model_validate(item)
    for item in load_fixture("prices.json"):
        PricePoint.model_validate(item)
