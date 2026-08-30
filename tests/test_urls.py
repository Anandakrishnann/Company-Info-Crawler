import pytest

from app.crawler.crawler import WebsiteCrawler
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
    
def test_homepage_has_highest_initial_priority():

    crawler = WebsiteCrawler(
        "https://example.com"
    )

    crawler._add_to_queue(
        "https://example.com/about",
        score=10,
    )

    crawler._add_to_queue(
        "https://example.com/contact",
        score=20,
    )

    item = crawler._get_next_url()

    assert item["url"] == (
        "https://example.com/"
    )
    
@pytest.mark.anyio
async def test_crawler_tracks_skipped_pages():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=1,
    )

    crawler._add_to_queue(
        "https://example.com/about",
        score=50,
    )

    crawler._add_to_queue(
        "https://example.com/contact",
        score=40,
    )

    pages, stats = await crawler.crawl()

    assert stats.crawled <= 1
    assert stats.skipped >= 0
    

from unittest.mock import AsyncMock, patch


@pytest.mark.anyio
async def test_crawler_handles_failed_page():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=1,
    )

    with patch(
        "app.crawler.crawler.fetch_page",
        new=AsyncMock(
            return_value=(
                500,
                "https://example.com/",
                "",
            )
        ),
    ):

        pages, stats = await crawler.crawl()

    assert stats.failed == 1
    assert stats.crawled == 0
    assert len(pages) == 1

    assert pages[0].processed is False
    

@pytest.mark.anyio
async def test_crawler_processes_successful_page():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=1,
    )

    html = """
    <html>
        <head>
            <title>Example Company</title>
        </head>
        <body>
            <a href="/about">About</a>
            <a href="/contact">Contact</a>
        </body>
    </html>
    """

    with patch(
        "app.crawler.crawler.fetch_page",
        new=AsyncMock(
            return_value=(
                200,
                "https://example.com/",
                html,
            )
        ),
    ):

        pages, stats = await crawler.crawl()

    assert stats.crawled == 1
    assert stats.failed == 0
    assert len(pages) == 1

    assert pages[0].processed is True
    assert pages[0].status_code == 200

    assert pages[0].extraction_result[
        "discovered_links"
    ] == 2
    
    
@pytest.mark.anyio
async def test_crawler_returns_page_metadata():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=1,
    )

    html = """
    <html>
        <head>
            <title>ABC Industries</title>
        </head>
        <body>
            <p>Industrial automation company.</p>
        </body>
    </html>
    """

    with patch(
        "app.crawler.crawler.fetch_page",
        new=AsyncMock(
            return_value=(
                200,
                "https://example.com/",
                html,
            )
        ),
    ):

        pages, stats = await crawler.crawl()

    assert len(pages) == 1
    assert pages[0].url == (
        "https://example.com/"
    )

    assert pages[0].status_code == 200
    assert pages[0].processed is True

    assert pages[0].extraction_result[
        "html_length"
    ] == len(html)
    
@pytest.mark.anyio
async def test_crawler_discovers_internal_links():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=1,
    )

    html = """
    <html>
        <body>
            <a href="/about">About</a>
            <a href="/products">Products</a>
        </body>
    </html>
    """

    with patch(
        "app.crawler.crawler.fetch_page",
        new=AsyncMock(
            return_value=(
                200,
                "https://example.com/",
                html,
            )
        ),
    ):

        pages, stats = await crawler.crawl()

    assert (
        "https://example.com/about"
        in crawler.visited
    )

    assert (
        "https://example.com/products"
        in crawler.visited
    )
    
@pytest.mark.anyio
async def test_crawler_discovers_internal_links():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=1,
    )

    html = """
    <html>
        <body>
            <a href="/about">About</a>
            <a href="/products">Products</a>
        </body>
    </html>
    """

    with patch(
        "app.crawler.crawler.fetch_page",
        new=AsyncMock(
            return_value=(
                200,
                "https://example.com/",
                html,
            )
        ),
    ):

        pages, stats = await crawler.crawl()

    assert (
        "https://example.com/about"
        in crawler.visited
    )

    assert (
        "https://example.com/products"
        in crawler.visited
    )
    
    
@pytest.mark.anyio
async def test_crawler_respects_max_pages():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=2,
    )

    html = """
    <html>
        <body>
            <a href="/about">About</a>
            <a href="/products">Products</a>
            <a href="/contact">Contact</a>
        </body>
    </html>
    """

    with patch(
        "app.crawler.crawler.fetch_page",
        new=AsyncMock(
            return_value=(
                200,
                "https://example.com/",
                html,
            )
        ),
    ):

        pages, stats = await crawler.crawl()

    assert stats.crawled == 2
    assert len(pages) == 2
    

@pytest.mark.anyio
async def test_crawler_does_not_crawl_external_links():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=5,
    )

    html = """
    <html>
        <body>
            <a href="/about">About</a>
            <a href="https://google.com">Google</a>
            <a href="https://github.com">GitHub</a>
        </body>
    </html>
    """

    with patch(
        "app.crawler.crawler.fetch_page",
        new=AsyncMock(
            return_value=(
                200,
                "https://example.com/",
                html,
            )
        ),
    ):

        pages, stats = await crawler.crawl()

    assert (
        "https://example.com/about"
        in crawler.visited
    )

    assert (
        "https://google.com"
        not in crawler.visited
    )

    assert (
        "https://github.com"
        not in crawler.visited
    )
    
@pytest.mark.anyio
async def test_crawler_handles_empty_html():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=1,
    )

    with patch(
        "app.crawler.crawler.fetch_page",
        new=AsyncMock(
            return_value=(
                200,
                "https://example.com/",
                "",
            )
        ),
    ):

        pages, stats = await crawler.crawl()

    assert stats.crawled == 0
    assert stats.failed == 1
    assert len(pages) == 1

    assert pages[0].processed is False
    assert pages[0].status_code == 200
    

@pytest.mark.anyio
async def test_crawler_preserves_final_url():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=1,
    )

    html = """
    <html>
        <head>
            <title>ABC Industries</title>
        </head>
        <body>
            <p>Company information.</p>
        </body>
    </html>
    """

    with patch(
        "app.crawler.crawler.fetch_page",
        new=AsyncMock(
            return_value=(
                200,
                "https://example.com/about",
                html,
            )
        ),
    ):

        pages, stats = await crawler.crawl()

    assert stats.crawled == 1
    assert len(pages) == 1

    assert pages[0].url == (
        "https://example.com/about"
    )