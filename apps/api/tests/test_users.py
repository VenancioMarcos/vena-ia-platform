def test_create_and_list_user(client) -> None:
    response = client.post(
        "/users", json={"name": "Ada Lovelace", "email": "ada@vena-ia.dev", "role": "admin"}
    )
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Ada Lovelace"
    assert created["role"] == "admin"

    listed = client.get("/users")
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_create_user_duplicate_email_conflicts(client) -> None:
    payload = {"name": "Grace Hopper", "email": "grace@vena-ia.dev", "role": "member"}
    first = client.post("/users", json=payload)
    assert first.status_code == 201

    second = client.post("/users", json=payload)
    assert second.status_code == 409


def test_get_user_not_found(client) -> None:
    response = client.get("/users/does-not-exist")
    assert response.status_code == 404
