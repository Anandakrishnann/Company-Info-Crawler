from bs4 import BeautifulSoup

from app.extraction.extractor import (
    extract_description,
    extract_emails,
    extract_phones,
    extract_social_profiles,
    extract_title,
)


HTML = """
<html>

<head>
    <title>ABC Industries</title>

    <meta
        name="description"
        content="ABC Industries provides industrial automation solutions."
    >
</head>

<body>

    <h1>ABC Industries</h1>

    <p>
        We provide industrial automation services
        to manufacturing companies worldwide.
    </p>

    <p>
        Contact us at info@abcindustries.com
    </p>

    <p>
        Phone: +91 98765 43210
    </p>

    <a href="mailto:sales@abcindustries.com">
        Email Sales
    </a>

    <a href="tel:+919876543210">
        Call Us
    </a>

    <a href="https://www.linkedin.com/company/abcindustries">
        LinkedIn
    </a>

    <a href="https://www.facebook.com/abcindustries">
        Facebook
    </a>

</body>

</html>
"""


def test_extract_title():

    soup = BeautifulSoup(
        HTML,
        "lxml",
    )

    assert extract_title(soup) == (
        "ABC Industries"
    )


def test_extract_description():

    soup = BeautifulSoup(
        HTML,
        "lxml",
    )

    description = extract_description(
        soup
    )

    assert (
        description
        == "ABC Industries provides industrial automation solutions."
    )


def test_extract_emails():

    soup = BeautifulSoup(
        HTML,
        "lxml",
    )

    emails = extract_emails(
        soup
    )

    assert emails == [
        "info@abcindustries.com",
        "sales@abcindustries.com",
    ]


def test_extract_phones():

    soup = BeautifulSoup(
        HTML,
        "lxml",
    )

    phones = extract_phones(
        soup
    )

    assert len(phones) >= 1


def test_extract_social_profiles():

    soup = BeautifulSoup(
        HTML,
        "lxml",
    )

    profiles = extract_social_profiles(
        soup,
        "https://abcindustries.com/",
    )

    platforms = {
        profile["platform"]
        for profile in profiles
    }

    assert "linkedin" in platforms
    assert "facebook" in platforms