def _create_project(client) -> str:
    user = client.post(
        "/users", json={"name": "Owner", "email": "owner2@vena-ia.dev", "role": "member"}
    ).json()
    project = client.post("/projects", json={"name": "Project X", "owner_id": user["id"]}).json()
    return project["id"]


def test_create_file_requires_existing_project(client) -> None:
    response = client.post(
        "/files", json={"project_id": "missing", "filename": "part.step", "type": "STEP"}
    )
    assert response.status_code == 404


def test_create_and_list_file(client) -> None:
    project_id = _create_project(client)

    created = client.post(
        "/files",
        json={"project_id": project_id, "filename": "bracket.step", "type": "STEP"},
    )
    assert created.status_code == 201

    listed = client.get("/files", params={"project_id": project_id})
    assert listed.status_code == 200
    assert len(listed.json()) == 1
    assert listed.json()[0]["filename"] == "bracket.step"
