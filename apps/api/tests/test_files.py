def _create_project(client, make_account, email: str):
    owner = make_account(email)
    project = client.post(
        "/projects",
        headers=owner.headers,
        json={"name": "Project X"},
    ).json()
    return project["id"], owner


def test_create_file_requires_existing_project(client, make_account) -> None:
    owner = make_account("file-missing@vena-ia.dev")

    response = client.post(
        "/files",
        headers=owner.headers,
        json={"project_id": "missing", "filename": "part.step", "type": "STEP"},
    )

    assert response.status_code == 404


def test_create_and_list_file(client, make_account) -> None:
    project_id, owner = _create_project(client, make_account, "file-owner@vena-ia.dev")

    created = client.post(
        "/files",
        headers=owner.headers,
        json={"project_id": project_id, "filename": "bracket.step", "type": "STEP"},
    )
    listed = client.get(
        "/files",
        headers=owner.headers,
        params={"project_id": project_id},
    )

    assert created.status_code == 201
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["filename"] == "bracket.step"


def test_file_metadata_is_hidden_from_another_owner(client, make_account) -> None:
    project_id, owner = _create_project(
        client,
        make_account,
        "private-file-owner@vena-ia.dev",
    )
    other = make_account("private-file-other@vena-ia.dev")
    client.post(
        "/files",
        headers=owner.headers,
        json={"project_id": project_id, "filename": "private.step", "type": "STEP"},
    )

    response = client.get(
        "/files",
        headers=other.headers,
        params={"project_id": project_id},
    )

    assert response.status_code == 404
