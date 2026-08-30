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