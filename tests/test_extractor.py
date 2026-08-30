from bs4 import BeautifulSoup

from app.extraction.extractor import (
    extract_description,
    extract_emails,
    extract_phones,
    extract_social_profiles,
    extract_title,
    extract_page_data,
    extract_company_name,
    extract_address,
    extract_contact_page,
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
    

def test_extract_page_data():

    data = extract_page_data(
        HTML,
        "https://abcindustries.com/contact",
        "contact",
    )

    assert data["name"] == (
        "ABC Industries"
    )

    assert data["description"] == (
        "ABC Industries provides industrial automation solutions."
    )

    assert "info@abcindustries.com" in (
        data["emails"]
    )

    assert data["contact_page"] == (
        "https://abcindustries.com/contact"
    )
    
    
def test_extract_company_name_from_json_ld():

    html = """
    <html>
        <head>
            <script type="application/ld+json">
            {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": "ABC Industries"
            }
            </script>
        </head>
        <body>
        </body>
    </html>
    """

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    assert extract_company_name(
        soup
    ) == "ABC Industries"

def test_extract_address():

    html = """
    <html>
        <body>
            <address>
                Kochi, Kerala, India
            </address>
        </body>
    </html>
    """

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    assert extract_address(
        soup
    ) == "Kochi, Kerala, India"

def test_extract_contact_page():

    html = """
    <html>
        <body>
            <a href="/contact-us">
                Contact Us
            </a>
        </body>
    </html>
    """

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    result = extract_contact_page(
        soup,
        "https://example.com/",
    )

    assert result == (
        "https://example.com/contact-us"
    )


def test_page_data_includes_contact_information():

    html = """
    <html>
        <head>
            <title>ABC Industries</title>
        </head>

        <body>

            <address>
                Kochi, Kerala, India
            </address>

            <a href="/contact">
                Contact Us
            </a>

        </body>
    </html>
    """

    data = extract_page_data(
        html,
        "https://example.com/about",
        "about",
    )

    assert data["address"] == (
        "Kochi, Kerala, India"
    )

    assert data["contact_page"] == (
        "https://example.com/contact"
    )