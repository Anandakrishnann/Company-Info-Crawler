from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_crawl_requires_url():

    response = client.post(
        "/crawl",
        json={},
    )

    assert response.status_code == 422