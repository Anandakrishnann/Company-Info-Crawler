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