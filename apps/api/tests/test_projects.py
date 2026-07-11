def _create_user(client) -> str:
    response = client.post(
        "/users", json={"name": "Owner", "email": "owner@vena-ia.dev", "role": "member"}
    )
    return response.json()["id"]


def test_create_project_requires_existing_owner(client) -> None:
    response = client.post("/projects", json={"name": "CNC Line A", "owner_id": "missing"})
    assert response.status_code == 404


def test_create_and_list_project(client) -> None:
    owner_id = _create_user(client)

    created = client.post("/projects", json={"name": "CNC Line A", "owner_id": owner_id})
    assert created.status_code == 201
    assert created.json()["owner_id"] == owner_id

    listed = client.get("/projects", params={"owner_id": owner_id})
    assert listed.status_code == 200
    assert len(listed.json()) == 1
