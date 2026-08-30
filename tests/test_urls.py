from app.crawler.url_manager import (
    calculate_relevance,
    extract_links,
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
    

def test_products_is_relevant():

    score = calculate_relevance(
        "https://example.com/products"
    )

    assert score >= 10


def test_services_is_relevant():

    score = calculate_relevance(
        "https://example.com/services"
    )

    assert score >= 10


def test_solutions_is_relevant():

    score = calculate_relevance(
        "https://example.com/solutions"
    )

    assert score >= 10


def test_industries_is_relevant():

    score = calculate_relevance(
        "https://example.com/industries"
    )

    assert score >= 10
    

def test_generic_page_has_low_relevance():

    score = calculate_relevance(
        "https://example.com/random-page"
    )

    assert score == 0
    
def test_anchor_text_can_increase_relevance():

    score = calculate_relevance(
        "https://example.com/catalog",
        anchor_text="Our Products",
    )

    assert score >= 9
    
    
def test_extract_links_prioritizes_company_pages():

    html = """
    <html>
        <body>

            <a href="/random-page">
                Random Page
            </a>

            <a href="/contact">
                Contact Us
            </a>

            <a href="/products">
                Our Products
            </a>

            <a href="https://google.com">
                Google
            </a>

            <a href="/brochure.pdf">
                Brochure
            </a>

        </body>
    </html>
    """

    links = extract_links(
        html=html,
        current_url="https://example.com/",
        base_domain="example.com",
    )

    urls = [
        link["url"]
        for link in links
    ]

    assert (
        "https://example.com/products"
        in urls
    )

    assert (
        "https://example.com/contact"
        in urls
    )

    assert (
        "https://example.com/random-page"
        in urls
    )

    assert (
        "https://google.com"
        not in urls
    )

    assert (
        "https://example.com/brochure.pdf"
        not in urls
    )

    assert links[0]["url"] == (
        "https://example.com/products"
    )
    
def test_extract_links_removes_duplicates():

    html = """
    <html>
        <body>

            <a href="/about">
                About
            </a>

            <a href="/about/">
                About Company
            </a>

            <a href="/about#team">
                Our Team
            </a>

        </body>
    </html>
    """

    links = extract_links(
        html=html,
        current_url="https://example.com/",
        base_domain="example.com",
    )

    urls = [
        link["url"]
        for link in links
    ]

    assert urls.count(
        "https://example.com/about"
    ) == 1

    assert len(links) == 1
    

def test_extract_links_resolves_relative_urls():

    html = """
    <html>
        <body>

            <a href="/about">
                About
            </a>

            <a href="products">
                Products
            </a>

        </body>
    </html>
    """

    links = extract_links(
        html=html,
        current_url="https://example.com/company/",
        base_domain="example.com",
    )

    urls = [
        link["url"]
        for link in links
    ]

    assert (
        "https://example.com/about"
        in urls
    )

    assert (
        "https://example.com/company/products"
        in urls
    )
    

def test_extract_links_ignores_non_http_links():

    html = """
    <html>
        <body>

            <a href="/about">
                About
            </a>

            <a href="mailto:info@example.com">
                Email
            </a>

            <a href="tel:+1234567890">
                Phone
            </a>

            <a href="javascript:void(0)">
                JavaScript
            </a>

        </body>
    </html>
    """

    links = extract_links(
        html=html,
        current_url="https://example.com/",
        base_domain="example.com",
    )

    urls = [
        link["url"]
        for link in links
    ]

    assert (
        "https://example.com/about"
        in urls
    )

    assert not any(
        url.startswith("mailto:")
        for url in urls
    )

    assert not any(
        url.startswith("tel:")
        for url in urls
    )

    assert not any(
        url.startswith("javascript:")
        for url in urls
    )
    

def test_extract_links_normalizes_tracking_parameters():

    html = """
    <html>
        <body>

            <a href="/about?utm_source=google">
                About
            </a>

            <a href="/about">
                About Company
            </a>

        </body>
    </html>
    """

    links = extract_links(
        html=html,
        current_url="https://example.com/",
        base_domain="example.com",
    )

    urls = [
        link["url"]
        for link in links
    ]

    assert (
        urls.count(
            "https://example.com/about"
        ) == 1
    )