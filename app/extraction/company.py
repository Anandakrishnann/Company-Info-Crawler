from bs4 import BeautifulSoup


def extract_company_info(html: str, url: str) -> dict:
    soup = BeautifulSoup(html, "lxml")

    title = soup.title.get_text(" ", strip=True) if soup.title else None

    description = None

    meta_description = soup.find(
        "meta",
        attrs={"name": "description"}
    )

    if meta_description:
        description = meta_description.get("content")

    if not description:
        first_paragraph = soup.find("p")

        if first_paragraph:
            description = first_paragraph.get_text(
                " ",
                strip=True
            )

    return {
        "name": title,
        "website": url,
        "description": description,
    }