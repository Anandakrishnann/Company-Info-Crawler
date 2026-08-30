from urllib.parse import urlparse


CATEGORY_KEYWORDS = {
    "about": {
        "about",
        "who we are",
        "who-we-are",
        "our story",
        "company profile",
        "company overview",
    },
    "products": {
        "product",
        "products",
        "product range",
        "product catalog",
        "product catalogue",
    },
    "services": {
        "service",
        "services",
        "what we do",
    },
    "solutions": {
        "solution",
        "solutions",
        "what we offer",
    },
    "industries": {
        "industry",
        "industries",
        "sectors",
        "markets",
    },
    "projects": {
        "project",
        "projects",
        "case study",
        "case studies",
        "portfolio",
    },
    "locations": {
        "location",
        "locations",
        "offices",
        "branches",
        "global presence",
    },
    "contact": {
        "contact",
        "contact us",
        "get in touch",
        "reach us",
    },
    "careers": {
        "career",
        "careers",
        "jobs",
        "join us",
        "work with us",
    },
    "blog": {
        "blog",
        "news",
        "article",
        "articles",
    },
}


def classify_page(
    url: str,
    title: str = "",
    headings: list[str] | None = None,
    anchor_text: str = "",
) -> str:

    headings = headings or []

    parsed = urlparse(url)

    path = parsed.path.lower()
    title_lower = title.lower()
    anchor_lower = anchor_text.lower()
    headings_lower = [
        heading.lower()
        for heading in headings
    ]

    scores = {
        category: 0
        for category in CATEGORY_KEYWORDS
    }

    for category, keywords in CATEGORY_KEYWORDS.items():

        for keyword in keywords:

            # URL is the strongest signal.
            if keyword in path:
                scores[category] += 5

            # Exact/strong title signal.
            if keyword in title_lower:
                scores[category] += 4

            # Headings are strong evidence of page purpose.
            for heading in headings_lower:
                if keyword in heading:
                    scores[category] += 4

            # Anchor text is useful but slightly weaker.
            if keyword in anchor_lower:
                scores[category] += 3

    best_category = max(
        scores,
        key=scores.get,
    )

    if scores[best_category] == 0:
        return "unknown"

    return best_category