def test_create_project_rejects_client_selected_owner(client, make_account) -> None:
    owner = make_account("owner-spoof@vena-ia.dev")

    response = client.post(
        "/projects",
        headers=owner.headers,
        json={"name": "CNC Line A", "owner_id": "forged-owner"},
    )

    assert response.status_code == 422


def test_create_and_list_own_project(client, make_account) -> None:
    owner = make_account("project-owner@vena-ia.dev")

    created = client.post(
        "/projects",
        headers=owner.headers,
        json={"name": "CNC Line A"},
    )
    listed = client.get("/projects", headers=owner.headers)

    assert created.status_code == 201
    assert created.json()["owner_id"] == owner.id
    assert listed.status_code == 200
    assert len(listed.json()) == 1


def test_project_is_hidden_from_another_user(client, make_account) -> None:
    owner = make_account("hidden-owner@vena-ia.dev")
    other = make_account("hidden-other@vena-ia.dev")
    project = client.post(
        "/projects",
        headers=owner.headers,
        json={"name": "Private Project"},
    ).json()

    fetched = client.get(f"/projects/{project['id']}", headers=other.headers)
    listed = client.get(
        "/projects",
        params={"owner_id": owner.id},
        headers=other.headers,
    )

    assert fetched.status_code == 404
    assert listed.status_code == 403


def test_admin_can_access_any_project(client, make_account) -> None:
    owner = make_account("admin-project-owner@vena-ia.dev")
    admin = make_account("admin-project@vena-ia.dev", role="admin")
    project = client.post(
        "/projects",
        headers=owner.headers,
        json={"name": "Admin Visible"},
    ).json()

    response = client.get(f"/projects/{project['id']}", headers=admin.headers)

    assert response.status_code == 200
