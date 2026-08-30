from urllib.parse import (
    parse_qsl,
    urlencode,
    urljoin,
    urlparse,
    urlunparse,
)

RELEVANT_KEYWORDS = {
    "about": 10,
    "company": 10,
    "products": 9,
    "product": 9,
    "services": 9,
    "service": 9,
    "solutions": 9,
    "solution": 9,
    "industries": 8,
    "industry": 8,
    "projects": 7,
    "project": 7,
    "locations": 8,
    "location": 8,
    "contact": 10,
    "leadership": 6,
    "management": 5,
    "team": 5,
}


IGNORED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    ".bmp",

    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",

    ".zip",
    ".rar",
    ".7z",

    ".mp3",
    ".wav",
    ".mp4",
    ".avi",
    ".mov",

    ".css",
    ".js",
    ".xml",
    ".json",
}


TRACKING_PARAMETERS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
}


def normalize_url(url: str) -> str:
    """
    Normalize a URL so equivalent URLs are treated
    as the same resource.
    """

    parsed = urlparse(url)

    scheme = parsed.scheme.lower()

    hostname = parsed.hostname

    if not hostname:
        return ""

    hostname = hostname.lower()

    # Preserve port when present.
    try:
        port = parsed.port
    except ValueError:
        port = None

    if port:
        hostname = f"{hostname}:{port}"

    path = parsed.path or "/"

    # Remove trailing slash except homepage.
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")

    # Remove tracking parameters.
    query_parts = []

    if parsed.query:
        for key, value in parse_qsl(
            parsed.query,
            keep_blank_values=True,
        ):
            if key.lower() not in TRACKING_PARAMETERS:
                query_parts.append((key, value))

    query = urlencode(query_parts)

    # Fragment is deliberately removed.
    return urlunparse(
        (
            scheme,
            hostname,
            path,
            "",
            query,
            "",
        )
    )


def is_http_url(url: str) -> bool:
    """
    Allow only HTTP and HTTPS URLs.
    """

    parsed = urlparse(url)

    return parsed.scheme.lower() in {
        "http",
        "https",
    }


def is_internal_url(
    url: str,
    base_domain: str,
) -> bool:
    """
    Determine whether a URL belongs to the same
    company website.
    """

    parsed = urlparse(url)

    hostname = parsed.hostname

    if not hostname:
        return False

    hostname = hostname.lower()

    return hostname == base_domain.lower()


def is_ignored_resource(url: str) -> bool:
    """
    Ignore files and resources that are not HTML pages.
    """

    parsed = urlparse(url)

    path = parsed.path.lower()

    return any(
        path.endswith(extension)
        for extension in IGNORED_EXTENSIONS
    )


def calculate_relevance(
    url: str,
    anchor_text: str = "",
) -> int:
    """
    Calculate how useful a URL is likely to be
    for company-information extraction.
    """

    parsed = urlparse(url)

    searchable_text = (
        f"{parsed.path} {anchor_text}"
    ).lower()

    score = 0

    for keyword, points in RELEVANT_KEYWORDS.items():
        if keyword in searchable_text:
            score += points

    return score


def extract_links(
    html: str,
    current_url: str,
    base_domain: str,
) -> list[dict]:
    """
    Extract useful internal links from an HTML page.
    """

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    discovered = []
    seen = set()

    for link in soup.find_all(
        "a",
        href=True,
    ):
        href = link.get("href")

        if not href:
            continue

        # Convert relative URLs to absolute URLs.
        absolute_url = urljoin(
            current_url,
            href,
        )

        # Normalize.
        normalized_url = normalize_url(
            absolute_url
        )

        if not normalized_url:
            continue

        # Only HTTP/HTTPS.
        if not is_http_url(normalized_url):
            continue

        # Only same-domain URLs.
        if not is_internal_url(
            normalized_url,
            base_domain,
        ):
            continue

        # Ignore files.
        if is_ignored_resource(
            normalized_url
        ):
            continue

        # Prevent duplicate URLs.
        if normalized_url in seen:
            continue

        seen.add(normalized_url)

        anchor_text = link.get_text(
            " ",
            strip=True,
        )

        score = calculate_relevance(
            normalized_url,
            anchor_text,
        )

        discovered.append(
            {
                "url": normalized_url,
                "anchor_text": anchor_text,
                "score": score,
            }
        )

    # Highest-value pages first.
    discovered.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    return discovered