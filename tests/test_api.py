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
    
    
def test_crawl_response_contains_contact_fields():

    response = client.post(
        "/crawl",
        json={
            "url": "https://example.com"
        },
    )

    assert response.status_code == 200

    contact = response.json()["contact"]

    expected_fields = {
        "emails",
        "phones",
        "address",
        "contact_page",
        "social_profiles",
    }

    assert expected_fields.issubset(
        contact.keys()
    )
    

def test_crawl_response_contains_stats():

    response = client.post(
        "/crawl",
        json={
            "url": "https://example.com"
        },
    )

    assert response.status_code == 200

    stats = response.json()["crawl_stats"]

    expected_fields = {
        "discovered",
        "crawled",
        "skipped",
        "failed",
    }

    assert expected_fields.issubset(
        stats.keys()
    )

    assert stats["crawled"] >= 1
    assert stats["failed"] == 0
    
def test_crawl_response_contains_stats():

    response = client.post(
        "/crawl",
        json={
            "url": "https://example.com"
        },
    )

    assert response.status_code == 200

    stats = response.json()["crawl_stats"]

    expected_fields = {
        "discovered",
        "crawled",
        "skipped",
        "failed",
    }

    assert expected_fields.issubset(
        stats.keys()
    )

    assert stats["crawled"] >= 1
    assert stats["failed"] == 0
    
    
def test_crawl_response_contains_pages():

    response = client.post(
        "/crawl",
        json={
            "url": "https://example.com"
        },
    )

    assert response.status_code == 200

    pages = response.json()["pages"]

    assert isinstance(pages, list)
    assert len(pages) >= 1

    page = pages[0]

    assert "url" in page
    assert "title" in page
    assert "category" in page
    assert "status_code" in page
    assert "processed" in page
    assert "extraction_result" in page
    
    
def test_crawl_page_is_processed():

    response = client.post(
        "/crawl",
        json={
            "url": "https://example.com"
        },
    )

    assert response.status_code == 200

    pages = response.json()["pages"]

    assert pages[0]["processed"] is True
    assert pages[0]["status_code"] == 200
    
    
    
def test_crawl_normalizes_homepage_url():

    response = client.post(
        "/crawl",
        json={
            "url": "https://example.com/"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["company"]["website"] == (
        "https://example.com/"
    )

    assert data["pages"][0]["url"] == (
        "https://example.com/"
    )
    
    
def test_crawl_rejects_invalid_url():

    response = client.post(
        "/crawl",
        json={
            "url": "not-a-valid-url"
        },
    )

    assert response.status_code == 422