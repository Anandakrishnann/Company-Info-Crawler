from app.extraction.aggregator import (
    CompanyAggregator,
    
    
)


def test_scalar_value_is_preserved():

    aggregator = CompanyAggregator()

    aggregator.add_page_data(
        {
            "name": "ABC Industries",
        },
        source_url="https://example.com/about",
    )

    aggregator.add_page_data(
        {
            "name": "Wrong Company Name",
        },
        source_url="https://example.com/contact",
    )

    result = aggregator.result()

    assert result["name"] == (
        "ABC Industries"
    )


def test_duplicate_products_are_removed():

    aggregator = CompanyAggregator()

    aggregator.add_page_data(
        {
            "products": [
                "PLC",
                "SCADA",
            ]
        }
    )

    aggregator.add_page_data(
        {
            "products": [
                "PLC",
                "Robotics",
            ]
        }
    )

    result = aggregator.result()

    assert result["products"] == [
        "PLC",
        "SCADA",
        "Robotics",
    ]


def test_duplicate_emails_are_removed():

    aggregator = CompanyAggregator()

    aggregator.add_page_data(
        {
            "emails": [
                "info@example.com",
            ]
        }
    )

    aggregator.add_page_data(
        {
            "emails": [
                "info@example.com",
                "sales@example.com",
            ]
        }
    )

    result = aggregator.result()

    assert result["emails"] == [
        "info@example.com",
        "sales@example.com",
    ]


def test_missing_fields_are_allowed():

    aggregator = CompanyAggregator()

    aggregator.add_page_data(
        {
            "name": "ABC Industries",
        }
    )

    result = aggregator.result()

    assert result["name"] == (
        "ABC Industries"
    )

    assert result["products"] == []

    assert result["services"] == []

    assert result["emails"] == []


def test_sources_are_recorded():

    aggregator = CompanyAggregator()

    aggregator.add_page_data(
        {
            "description": "Industrial automation company.",
        },
        source_url="https://example.com/about",
    )

    sources = aggregator.source_map()

    assert sources["description"] == [
        "https://example.com/about"
    ]

def test_description_conflict_keeps_first_value():

    aggregator = CompanyAggregator()

    aggregator.add_page_data(
        {
            "name": "ABC Industries",
            "website": "https://abcindustries.com/",
            "description": (
                "ABC Industries is a manufacturer."
            ),
        },
        "https://abcindustries.com/about",
    )

    aggregator.add_page_data(
        {
            "name": "ABC Industries",
            "website": "https://abcindustries.com/",
            "description": (
                "ABC Industries is a technology company."
            ),
        },
        "https://abcindustries.com/contact",
    )

    result = aggregator.result()

    assert result["description"] == (
        "ABC Industries is a manufacturer."
    )