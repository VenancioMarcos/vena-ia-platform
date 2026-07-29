def _create_project(client, make_account, email: str):
    owner = make_account(email)
    project = client.post(
        "/projects",
        headers=owner.headers,
        json={"name": "Project Y"},
    ).json()
    return project["id"], owner


def test_messages_require_existing_project(client, make_account) -> None:
    owner = make_account("chat-missing@vena-ia.dev")

    response = client.get("/chat/missing/messages", headers=owner.headers)

    assert response.status_code == 404


def test_create_and_list_messages(client, make_account) -> None:
    project_id, owner = _create_project(client, make_account, "chat-owner@vena-ia.dev")

    empty = client.get(f"/chat/{project_id}/messages", headers=owner.headers)
    created = client.post(
        f"/chat/{project_id}/messages",
        headers=owner.headers,
        json={"role": "user", "content": "Ola, Vena_IA!"},
    )
    listed = client.get(f"/chat/{project_id}/messages", headers=owner.headers)

    assert empty.status_code == 200
    assert empty.json() == []
    assert created.status_code == 201
    assert created.json()["role"] == "user"
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_create_message_rejects_invalid_role(client, make_account) -> None:
    project_id, owner = _create_project(
        client,
        make_account,
        "chat-invalid-role@vena-ia.dev",
    )

    response = client.post(
        f"/chat/{project_id}/messages",
        headers=owner.headers,
        json={"role": "system", "content": "x"},
    )

    assert response.status_code == 422


def test_chat_is_hidden_from_another_owner(client, make_account) -> None:
    project_id, _owner = _create_project(
        client,
        make_account,
        "private-chat-owner@vena-ia.dev",
    )
    other = make_account("private-chat-other@vena-ia.dev")

    response = client.get(f"/chat/{project_id}/messages", headers=other.headers)

    assert response.status_code == 404
