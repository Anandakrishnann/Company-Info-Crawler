from unittest.mock import AsyncMock
from unittest.mock import AsyncMock, patch
import pytest

from app.crawler.crawler import WebsiteCrawler


def test_crawler_initialization():

    crawler = WebsiteCrawler(
        "https://example.com"
    )

    assert crawler.start_url == (
        "https://example.com/"
    )

    assert crawler.base_domain == (
        "example.com"
    )

    assert crawler.max_pages == 20

    assert len(crawler.queue) == 1


def test_duplicate_urls_are_not_added():

    crawler = WebsiteCrawler(
        "https://example.com"
    )

    crawler._add_to_queue(
        "https://example.com/about",
        score=10,
    )

    crawler._add_to_queue(
        "https://example.com/about/",
        score=10,
    )

    assert len(crawler.visited) == 2


@pytest.mark.anyio
async def test_crawler_example_domain():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=5,
    )

    pages, stats = await crawler.crawl()

    assert stats.crawled >= 1

    assert len(pages) >= 1
    

def test_non_html_resources_are_not_added():

    crawler = WebsiteCrawler(
        "https://example.com"
    )

    crawler._add_to_queue(
        "https://example.com/company.pdf",
        score=10,
    )

    crawler._add_to_queue(
        "https://example.com/logo.png",
        score=10,
    )

    crawler._add_to_queue(
        "https://example.com/brochure.zip",
        score=10,
    )

    assert (
        "https://example.com/company.pdf"
        not in crawler.visited
    )

    assert (
        "https://example.com/logo.png"
        not in crawler.visited
    )

    assert (
        "https://example.com/brochure.zip"
        not in crawler.visited
    )
    

def test_tracking_query_urls_are_deduplicated():

    crawler = WebsiteCrawler(
        "https://example.com"
    )

    crawler._add_to_queue(
        "https://example.com/about?utm_source=google",
        score=10,
    )

    crawler._add_to_queue(
        "https://example.com/about?utm_source=facebook",
        score=10,
    )

    assert len(crawler.visited) == 2
    
def test_meaningful_query_parameters_are_preserved():

    crawler = WebsiteCrawler(
        "https://example.com"
    )

    crawler._add_to_queue(
        "https://example.com/products?category=pumps",
        score=10,
    )

    crawler._add_to_queue(
        "https://example.com/products?category=valves",
        score=10,
    )

    assert (
        "https://example.com/products?category=pumps"
        in crawler.visited
    )

    assert (
        "https://example.com/products?category=valves"
        in crawler.visited
    )
    

def test_fragment_urls_are_deduplicated():

    crawler = WebsiteCrawler(
        "https://example.com"
    )

    crawler._add_to_queue(
        "https://example.com/about#team",
        score=10,
    )

    crawler._add_to_queue(
        "https://example.com/about#contact",
        score=10,
    )

    assert (
        "https://example.com/about"
        in crawler.visited
    )

    assert len(crawler.visited) == 2
    
    
def test_highest_score_url_is_selected_first():

    crawler = WebsiteCrawler(
        "https://example.com"
    )

    # Remove the automatically queued homepage
    crawler.queue.clear()

    crawler._add_to_queue(
        "https://example.com/contact",
        score=20,
    )

    crawler._add_to_queue(
        "https://example.com/products",
        score=80,
    )

    crawler._add_to_queue(
        "https://example.com/about",
        score=50,
    )

    item = crawler._get_next_url()

    assert item["url"] == (
        "https://example.com/products"
    )

    assert item["score"] == 80
    

@pytest.mark.anyio
async def test_crawler_respects_max_pages():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=1,
    )

    pages, stats = await crawler.crawl()

    assert stats.crawled <= 1
    assert len(pages) <= 1
    

def test_crawler_only_accepts_internal_domain():

    crawler = WebsiteCrawler(
        "https://example.com"
    )

    crawler._add_to_queue(
        "https://example.com/products",
        score=50,
    )

    crawler._add_to_queue(
        "https://google.com",
        score=100,
    )

    assert (
        "https://example.com/products"
        in crawler.visited
    )

    assert (
        "https://google.com"
        not in crawler.visited
    )
    
@pytest.mark.anyio
async def test_crawler_handles_http_error_status():

    crawler = WebsiteCrawler(
        "https://example.com",
        max_pages=1,
    )

    mock_fetch = AsyncMock(
        return_value=(
            403,
            "https://example.com/",
            "<html><title>Access Denied</title></html>",
        )
    )

    with patch(
        "app.crawler.crawler.fetch_page",
        mock_fetch,
    ):

        pages, stats = await crawler.crawl()

    assert stats.crawled == 0
    assert stats.failed == 1

    assert len(pages) == 1
    assert pages[0].status_code == 403
    assert pages[0].processed is False