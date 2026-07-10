from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_foundation_routes() -> None:
    for path in ["/users", "/projects", "/files", "/chat"]:
        response = client.get(path)
        assert response.status_code == 200

