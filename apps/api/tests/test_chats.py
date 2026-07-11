def _create_project(client) -> str:
    user = client.post(
        "/users", json={"name": "Owner", "email": "owner3@vena-ia.dev", "role": "member"}
    ).json()
    project = client.post("/projects", json={"name": "Project Y", "owner_id": user["id"]}).json()
    return project["id"]


def test_messages_require_existing_project(client) -> None:
    response = client.get("/chat/missing/messages")
    assert response.status_code == 404


def test_create_and_list_messages(client) -> None:
    project_id = _create_project(client)

    empty = client.get(f"/chat/{project_id}/messages")
    assert empty.status_code == 200
    assert empty.json() == []

    created = client.post(
        f"/chat/{project_id}/messages", json={"role": "user", "content": "Ola, Vena_IA!"}
    )
    assert created.status_code == 201
    assert created.json()["role"] == "user"

    listed = client.get(f"/chat/{project_id}/messages")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_create_message_rejects_invalid_role(client) -> None:
    project_id = _create_project(client)

    response = client.post(
        f"/chat/{project_id}/messages", json={"role": "system", "content": "x"}
    )
    assert response.status_code == 422
