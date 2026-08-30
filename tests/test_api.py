from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_crawl_requires_url():

    response = client.post(
        "/crawl",
        json={},
    )

    assert response.status_code == 422
    

def test_crawl_accepts_valid_url():

    response = client.post(
        "/crawl",
        json={
            "url": "https://example.com"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "company" in data
    assert "contact" in data
    assert "pages" in data
    assert "crawl_stats" in data
    

def test_crawl_response_contains_company_fields():

    response = client.post(
        "/crawl",
        json={
            "url": "https://example.com"
        },
    )

    assert response.status_code == 200

    company = response.json()["company"]

    expected_fields = {
        "name",
        "website",
        "description",
        "headquarters",
        "locations",
        "products",
        "services",
        "solutions",
        "industries",
    }

    assert expected_fields.issubset(
        company.keys()
    )