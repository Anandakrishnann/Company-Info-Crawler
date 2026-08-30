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