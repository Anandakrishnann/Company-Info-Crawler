from app.extraction.aggregator import (
    CompanyAggregator,
    aggregate_company_data,
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
    

def test_scalar_field_source_is_recorded():

    aggregator = CompanyAggregator()

    source_url = (
        "https://abcindustries.com/about"
    )

    aggregator.add_page_data(
        {
            "name": "ABC Industries",
            "website": "https://abcindustries.com/",
            "description": (
                "ABC Industries is a manufacturer."
            ),
        },
        source_url,
    )

    sources = aggregator.source_map()

    assert sources["description"] == [
        source_url
    ]
    

def test_list_field_source_is_recorded():

    aggregator = CompanyAggregator()

    source_url = (
        "https://abcindustries.com/products"
    )

    aggregator.add_page_data(
        {
            "products": [
                "Industrial Pumps",
                "Control Systems",
            ],
        },
        source_url,
    )

    sources = aggregator.source_map()

    assert sources["products"] == [
        source_url
    ]
    

def test_duplicate_list_value_keeps_multiple_sources():

    aggregator = CompanyAggregator()

    first_url = (
        "https://abcindustries.com/about"
    )

    second_url = (
        "https://abcindustries.com/products"
    )

    aggregator.add_page_data(
        {
            "products": [
                "Industrial Pumps",
            ],
        },
        first_url,
    )

    aggregator.add_page_data(
        {
            "products": [
                "Industrial Pumps",
            ],
        },
        second_url,
    )

    result = aggregator.result()
    sources = aggregator.source_map()

    assert result["products"] == [
        "Industrial Pumps"
    ]

    assert sources["products"] == [
        first_url,
        second_url,
    ]
    


def test_missing_scalar_does_not_overwrite_existing_value():

    aggregator = CompanyAggregator()

    aggregator.add_page_data(
        {
            "description": (
                "ABC Industries is a manufacturer."
            ),
        },
        "https://abcindustries.com/about",
    )

    aggregator.add_page_data(
        {
            "description": None,
        },
        "https://abcindustries.com/contact",
    )

    result = aggregator.result()

    assert result["description"] == (
        "ABC Industries is a manufacturer."
    )
    
def test_aggregator_merges_multiple_pages():

    pages = [
        {
            "url": "https://example.com/products",
            "category": "products",
            "data": {
                "name": "ABC Industries",
                "website": "https://example.com/",
                "description": "Industrial company.",
                "headquarters": None,
                "locations": [],
                "products": [
                    "Industrial Pumps",
                    "Control Systems",
                ],
                "services": [],
                "solutions": [],
                "industries": [],
                "emails": [],
                "phones": [],
                "address": None,
                "contact_page": None,
                "social_profiles": [],
            },
        },
        {
            "url": "https://example.com/services",
            "category": "services",
            "data": {
                "name": "ABC Industries",
                "website": "https://example.com/",
                "description": "Another description.",
                "headquarters": None,
                "locations": [],
                "products": [],
                "services": [
                    "Installation",
                    "Maintenance",
                ],
                "solutions": [],
                "industries": [],
                "emails": [],
                "phones": [],
                "address": None,
                "contact_page": None,
                "social_profiles": [],
            },
        },
    ]

    result = aggregate_company_data(pages)

    assert "Industrial Pumps" in result["products"]
    assert "Control Systems" in result["products"]

    assert "Installation" in result["services"]
    assert "Maintenance" in result["services"]

    assert result["name"] == "ABC Industries"
    
    

def test_aggregator_removes_duplicate_list_values():

    pages = [
        {
            "url": "https://example.com/products",
            "data": {
                "products": [
                    "Industrial Pumps",
                    "Control Systems",
                ],
            },
        },
        {
            "url": "https://example.com/services",
            "data": {
                "products": [
                    "Industrial Pumps",
                    "Hydraulic Pumps",
                ],
            },
        },
    ]

    result = aggregate_company_data(pages)

    assert result["products"] == [
        "Industrial Pumps",
        "Control Systems",
        "Hydraulic Pumps",
    ]
    

def test_aggregator_ignores_empty_values():

    aggregator = CompanyAggregator()

    aggregator.add_page_data(
        {
            "name": "",
            "website": "   ",
            "description": None,
            "products": [
                "",
                "   ",
                "Industrial Pumps",
            ],
            "services": [],
            "emails": [
                "",
                "info@example.com",
            ],
        },
        "https://example.com/products",
    )

    result = aggregator.result()

    assert result["name"] is None
    assert result["website"] is None
    assert result["description"] is None

    assert result["products"] == [
        "Industrial Pumps"
    ]

    assert result["emails"] == [
        "info@example.com"
    ]
    
def test_aggregator_tracks_source_urls():

    aggregator = CompanyAggregator()

    aggregator.add_page_data(
        {
            "name": "ABC Industries",
            "description": "Industrial company.",
        },
        "https://example.com/about",
    )

    sources = aggregator.source_map()

    assert sources["name"] == [
        "https://example.com/about"
    ]

    assert sources["description"] == [
        "https://example.com/about"
    ]
    
    
def test_aggregator_preserves_first_contact_page():

    aggregator = CompanyAggregator()

    aggregator.add_page_data(
        {
            "contact_page": (
                "https://example.com/contact"
            ),
        },
        "https://example.com/contact",
    )

    aggregator.add_page_data(
        {
            "contact_page": (
                "https://example.com/contact-us"
            ),
        },
        "https://example.com/contact-us",
    )

    result = aggregator.result()

    assert result["contact_page"] == (
        "https://example.com/contact"
    )
    
def test_aggregator_merges_unique_social_profiles():

    pages = [
        {
            "url": "https://example.com/about",
            "data": {
                "social_profiles": [
                    "https://linkedin.com/company/abc",
                    "https://facebook.com/abc",
                ],
            },
        },
        {
            "url": "https://example.com/contact",
            "data": {
                "social_profiles": [
                    "https://linkedin.com/company/abc",
                    "https://twitter.com/abc",
                ],
            },
        },
    ]

    result = aggregate_company_data(pages)

    assert result["social_profiles"] == [
        "https://linkedin.com/company/abc",
        "https://facebook.com/abc",
        "https://twitter.com/abc",
    ]