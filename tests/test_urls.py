from app.crawler.url_manager import (
    calculate_relevance,
    is_http_url,
    is_ignored_resource,
    is_internal_url,
    normalize_url,
)


def test_fragment_is_removed():
    url = "https://example.com/about#team"

    assert normalize_url(url) == (
        "https://example.com/about"
    )


def test_trailing_slash_is_removed():
    url = "https://example.com/about/"

    assert normalize_url(url) == (
        "https://example.com/about"
    )


def test_homepage_slash_is_preserved():
    url = "https://example.com/"

    assert normalize_url(url) == (
        "https://example.com/"
    )


def test_tracking_parameters_are_removed():
    url = (
        "https://example.com/about"
        "?utm_source=google"
        "&utm_campaign=test"
    )

    assert normalize_url(url) == (
        "https://example.com/about"
    )


def test_normal_query_parameter_is_kept():
    url = (
        "https://example.com/products"
        "?category=software"
    )

    assert normalize_url(url) == (
        "https://example.com/products"
        "?category=software"
    )


def test_internal_url():
    assert is_internal_url(
        "https://example.com/about",
        "example.com",
    )


def test_external_url():
    assert not is_internal_url(
        "https://google.com",
        "example.com",
    )


def test_http_url():
    assert is_http_url(
        "https://example.com"
    )


def test_mailto_is_not_http():
    assert not is_http_url(
        "mailto:test@example.com"
    )


def test_pdf_is_ignored():
    assert is_ignored_resource(
        "https://example.com/company.pdf"
    )


def test_image_is_ignored():
    assert is_ignored_resource(
        "https://example.com/logo.png"
    )


def test_about_is_relevant():
    score = calculate_relevance(
        "https://example.com/about"
    )

    assert score >= 10


def test_contact_is_relevant():
    score = calculate_relevance(
        "https://example.com/contact"
    )

    assert score >= 10