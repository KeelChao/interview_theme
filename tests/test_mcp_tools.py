from mineral_daily_agent.servers.lme_price import get_trend
from mineral_daily_agent.servers.mineral_pdf import extract_resources
from mineral_daily_agent.servers.mining_news import search


def test_required_tool_functions_return_fixture_data() -> None:
    news = search("Pilbara lithium", days=7)
    resources = extract_resources("https://www.pilbaraminerals.com.au/fixture/pilgangoora-resources.pdf")
    trend = get_trend("lithium", days=7)

    assert news
    assert isinstance(resources, list)
    assert trend["commodity"] == "lithium"
