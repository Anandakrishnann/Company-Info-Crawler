import json
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup


EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+"
    r"@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
)

PHONE_PATTERN = re.compile(
    r"""
    (?:
        \+?\d{1,3}[\s.-]?
    )?
    (?:
        \(\d{2,4}\)[\s.-]?
    )?
    \d{3,4}[\s.-]?\d{3,4}
    """,
    re.VERBOSE,
)


SOCIAL_DOMAINS = {
    "linkedin.com": "linkedin",
    "facebook.com": "facebook",
    "instagram.com": "instagram",
    "twitter.com": "twitter",
    "x.com": "x",
    "youtube.com": "youtube",
}


def clean_text(text: str) -> str:
    """
    Normalize whitespace in extracted text.
    """

    return re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

def extract_company_name(
    soup: BeautifulSoup,
) -> str | None:
    """
    Extract company name using several signals.

    Priority:
    1. JSON-LD Organization name
    2. OpenGraph site name
    3. Header/logo text
    4. H1
    """

    # 1. JSON-LD structured data.
    for script in soup.find_all(
        "script",
        type="application/ld+json",
    ):
        try:
            data = json.loads(
                script.string or script.get_text()
            )
        except (json.JSONDecodeError, TypeError):
            continue

        candidates = []

        if isinstance(data, dict):
            candidates.append(data)

            graph = data.get("@graph")

            if isinstance(graph, list):
                candidates.extend(graph)

        elif isinstance(data, list):
            candidates.extend(data)

        for item in candidates:

            if not isinstance(item, dict):
                continue

            item_type = item.get("@type", "")

            if isinstance(item_type, list):
                is_org = any(
                    "organization" in str(t).lower()
                    for t in item_type
                )
            else:
                is_org = (
                    "organization"
                    in str(item_type).lower()
                )

            if is_org and item.get("name"):
                return clean_text(
                    str(item["name"])
                )

    # 2. OpenGraph site name.
    og_site = soup.find(
        "meta",
        property="og:site_name",
    )

    if og_site and og_site.get("content"):
        return clean_text(
            og_site["content"]
        )

    # 3. Header/logo text.
    header = soup.find("header")

    if header:

        logo = header.find(
            class_=re.compile(
                r"logo|brand",
                re.IGNORECASE,
            )
        )

        if logo:
            text = clean_text(
                logo.get_text(
                    " ",
                    strip=True,
                )
            )

            if text:
                return text

    # 4. H1.
    h1 = soup.find("h1")

    if h1:
        text = clean_text(
            h1.get_text(
                " ",
                strip=True,
            )
        )

        if text:
            return text

    return None


def extract_address(
    soup: BeautifulSoup,
) -> str | None:
    """
    Extract a likely physical company address.

    Priority:
    1. Semantic <address> element
    2. Elements with address/location-related classes
    """

    # 1. Semantic HTML address element
    address = soup.find("address")

    if address:
        text = clean_text(
            address.get_text(
                " ",
                strip=True,
            )
        )

        if text:
            return text

    # 2. Common address/location classes
    element = soup.find(
        class_=re.compile(
            r"address|location",
            re.IGNORECASE,
        )
    )

    if element:
        text = clean_text(
            element.get_text(
                " ",
                strip=True,
            )
        )

        if 10 <= len(text) <= 500:
            return text

    return None

def extract_contact_page(
    soup: BeautifulSoup,
    base_url: str,
) -> str | None:
    """
    Find a likely contact page from links.
    """

    contact_keywords = {
        "contact",
        "contact us",
        "get in touch",
        "reach us",
    }

    for link in soup.find_all(
        "a",
        href=True,
    ):
        text = clean_text(
            link.get_text(
                " ",
                strip=True,
            )
        ).lower()

        href = link["href"].strip()

        href_lower = href.lower()

        if (
            text in contact_keywords
            or "contact" in href_lower
        ):
            return urljoin(
                base_url,
                href,
            )

    return None

def extract_title(
    soup: BeautifulSoup,
) -> str | None:
    """
    Extract the HTML page title.
    """

    if not soup.title:
        return None

    title = clean_text(
        soup.title.get_text(
            " ",
            strip=True,
        )
    )

    return title or None


def extract_description(
    soup: BeautifulSoup,
) -> str | None:
    """
    Extract a useful page description.

    Priority:
    1. meta description
    2. first meaningful paragraph
    """

    meta = soup.find(
        "meta",
        attrs={
            "name": re.compile(
                "^description$",
                re.IGNORECASE,
            )
        },
    )

    if meta and meta.get("content"):
        description = clean_text(
            meta["content"]
        )

        if description:
            return description

    for paragraph in soup.find_all("p"):

        text = clean_text(
            paragraph.get_text(
                " ",
                strip=True,
            )
        )

        if len(text) >= 40:
            return text

    return None


def extract_emails(
    soup: BeautifulSoup,
) -> list[str]:
    """
    Extract email addresses from visible text
    and mailto links.
    """

    emails = set()

    # Visible page text.
    text = soup.get_text(
        " ",
        strip=True,
    )

    for email in EMAIL_PATTERN.findall(text):
        emails.add(email.lower())

    # mailto links.
    for link in soup.find_all(
        "a",
        href=True,
    ):
        href = link["href"]

        if href.lower().startswith("mailto:"):

            email = href[
                7:
            ].split("?")[0].strip()

            if EMAIL_PATTERN.fullmatch(email):
                emails.add(email.lower())

    return sorted(emails)


def extract_phones(
    soup: BeautifulSoup,
) -> list[str]:
    """
    Extract likely phone numbers.
    """

    phones = set()

    text = soup.get_text(
        " ",
        strip=True,
    )

    for match in PHONE_PATTERN.findall(text):

        phone = clean_text(match)

        # Avoid treating tiny numbers as phones.
        digits = re.sub(
            r"\D",
            "",
            phone,
        )

        if len(digits) >= 7:
            phones.add(phone)

    # Also inspect tel links.
    for link in soup.find_all(
        "a",
        href=True,
    ):
        href = link["href"]

        if href.lower().startswith("tel:"):

            phone = href[
                4:
            ].strip()

            if phone:
                phones.add(phone)

    return sorted(phones)


def extract_social_profiles(
    soup: BeautifulSoup,
    base_url: str,
) -> list[dict]:
    """
    Extract links to company social profiles.
    """

    profiles = []

    seen = set()

    for link in soup.find_all(
        "a",
        href=True,
    ):

        href = link["href"].strip()

        absolute_url = urljoin(
            base_url,
            href,
        )

        lower_url = absolute_url.lower()

        for domain, platform in SOCIAL_DOMAINS.items():

            if domain in lower_url:

                if absolute_url not in seen:

                    profiles.append(
                        {
                            "platform": platform,
                            "url": absolute_url,
                        }
                    )

                    seen.add(
                        absolute_url
                    )

                break

    return profiles


def extract_page_data(
    html: str,
    url: str,
    category: str,
) -> dict:
    """
    Extract structured information from a single
    crawled page.
    """

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    data = {
        "name": extract_company_name(soup),
        "website": url,
        "description": extract_description(soup),
        "headquarters": None,
        "locations": [],
        "products": [],
        "services": [],
        "solutions": [],
        "industries": [],
        "emails": extract_emails(soup),
        "phones": extract_phones(soup),
        "address": extract_address(soup),
        "contact_page": extract_contact_page(soup, url),
        "social_profiles": extract_social_profiles(soup,url,),
    }

    # Common extraction.
    title = extract_title(soup)

    description = extract_description(
        soup
    )

    emails = extract_emails(soup)

    phones = extract_phones(soup)

    social_profiles = extract_social_profiles(
        soup,
        url,
    )

    data["description"] = description
    data["emails"] = emails
    data["phones"] = phones
    data["social_profiles"] = social_profiles

    # Company name.
    if title:
        data["name"] = title

    # Contact page.
    if category == "contact":
        data["contact_page"] = url

    return data


def extract_category_items(
    soup: BeautifulSoup,
    category: str,
) -> list[str]:
    """
    Extract likely items for a specific page category.

    Uses headings and list items while filtering out
    common navigation and boilerplate text.
    """

    category_keywords = {
        "products": {
            "product",
            "products",
            "product range",
            "product portfolio",
        },
        "services": {
            "service",
            "services",
            "what we do",
            "our services",
        },
        "solutions": {
            "solution",
            "solutions",
            "our solutions",
        },
        "industries": {
            "industry",
            "industries",
            "sectors",
            "markets",
        },
    }

    keywords = category_keywords.get(
        category,
        set(),
    )

    candidates = []

    # Collect headings.
    for tag in soup.find_all(
        ["h2", "h3"]
    ):
        text = clean_text(
            tag.get_text(
                " ",
                strip=True,
            )
        )

        if not text:
            continue

        lower_text = text.lower()

        # Ignore headings that are simply
        # the category title itself.
        if lower_text in keywords:
            continue

        candidates.append(text)

    # Collect list items.
    for tag in soup.find_all("li"):
        text = clean_text(
            tag.get_text(
                " ",
                strip=True,
            )
        )

        if not text:
            continue

        if len(text) < 3 or len(text) > 150:
            continue

        candidates.append(text)

    # Remove duplicates while preserving order.
    result = []

    for item in candidates:

        if item not in result:
            result.append(item)

    return result