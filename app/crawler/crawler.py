from collections import deque
from urllib.parse import urlparse

from app.crawler.http_client import fetch_page
from app.crawler.url_manager import (
    extract_links,
    normalize_url,
)
from app.models.schemas import (
    CrawlStats,
    PageResult,
)


class WebsiteCrawler:
    """
    Crawls a company website and discovers useful
    internal pages.
    """

    def __init__(
        self,
        start_url: str,
        max_pages: int = 20,
    ):
        self.start_url = normalize_url(start_url)
        self.max_pages = max_pages

        parsed = urlparse(self.start_url)

        self.base_domain = (
            parsed.hostname.lower()
            if parsed.hostname
            else ""
        )

        # URLs waiting to be crawled.
        self.queue = deque()

        # URLs already scheduled.
        self.visited = set()

        # Results for crawled pages.
        self.pages = []

        self.stats = CrawlStats()

        # Homepage gets the highest priority.
        self._add_to_queue(
            self.start_url,
            score=100,
        )

    def _add_to_queue(
        self,
        url: str,
        score: int = 0,
    ):
        """
        Add a URL to the queue only if it hasn't
        already been scheduled and appears to be
        an HTML page.
        """

        normalized = normalize_url(url)

        if not normalized:
            return

        # Ignore non-HTML resources.
        ignored_extensions = {
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".webp",
            ".svg",
            ".zip",
            ".rar",
            ".7z",
            ".mp3",
            ".mp4",
            ".avi",
            ".mov",
            ".doc",
            ".docx",
            ".xls",
            ".xlsx",
            ".ppt",
            ".pptx",
        }

        path = urlparse(normalized).path.lower()

        if any(
            path.endswith(extension)
            for extension in ignored_extensions
        ):
            return

        if normalized in self.visited:
            return

        self.visited.add(normalized)

        self.queue.append(
            {
                "url": normalized,
                "score": score,
            }
        )

        self.stats.discovered += 1
    def _get_next_url(self):
        """
        Return the highest-priority URL.
        """

        if not self.queue:
            return None

        best_item = max(
            self.queue,
            key=lambda item: item["score"],
        )

        self.queue.remove(best_item)

        return best_item

    async def crawl(self):
        """
        Crawl until the queue is empty or max_pages
        has been reached.
        """

        while (
            self.queue
            and self.stats.crawled < self.max_pages
        ):
            item = self._get_next_url()

            if not item:
                break

            url = item["url"]

            status_code, final_url, html = (
                await fetch_page(url)
            )

            # Request failed or content wasn't HTML.
            if not html or status_code >= 400:
                self.stats.failed += 1

                self.pages.append(
                    PageResult(
                        url=final_url,
                        title=None,
                        category="unknown",
                        status_code=status_code,
                        processed=False,
                        extraction_result={
                            "error": (
                                "Page could not be "
                                "processed"
                            )
                        },
                    )
                )

                continue

            self.stats.crawled += 1

            # Discover links.
            links = extract_links(
                html=html,
                current_url=final_url,
                base_domain=self.base_domain,
            )

            # Add discovered links to queue.
            for link in links:
                self._add_to_queue(
                    link["url"],
                    link["score"],
                )

            # Temporary page result.
            page = PageResult(
                url=final_url,
                title=None,
                category="unknown",
                status_code=status_code,
                processed=True,
                extraction_result={
                    "discovered_links": len(links),
                    "html_length": len(html),
                },
            )

            self.pages.append(page)

        # URLs remaining in queue were not processed.
        self.stats.skipped = len(self.queue)

        return self.pages, self.stats