from app.extraction.classifier import classify_page


def test_about_page():

    result = classify_page(
        "https://example.com/about",
        title="About Us",
    )

    assert result == "about"


def test_products_page():

    result = classify_page(
        "https://example.com/products",
        title="Our Products",
    )

    assert result == "products"


def test_services_page():

    result = classify_page(
        "https://example.com/services",
        title="Our Services",
    )

    assert result == "services"


def test_contact_page():

    result = classify_page(
        "https://example.com/contact",
        title="Contact Us",
    )

    assert result == "contact"


def test_locations_page():

    result = classify_page(
        "https://example.com/locations",
        title="Our Locations",
    )

    assert result == "locations"


def test_unknown_page():

    result = classify_page(
        "https://example.com/random-page",
        title="Random Page",
    )

    assert result == "unknown"


def test_heading_can_help():

    result = classify_page(
        "https://example.com/company-profile",
        title="ABC Industries",
        headings=["Who We Are"],
    )

    assert result == "about"