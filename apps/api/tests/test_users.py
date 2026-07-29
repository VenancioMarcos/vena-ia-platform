from conftest import TEST_PASSWORD


def test_public_registration_creates_member_and_admin_can_list(client, make_account) -> None:
    response = client.post(
        "/users",
        json={
            "name": "Ada Lovelace",
            "email": "ada@vena-ia.dev",
            "password": TEST_PASSWORD,
        },
    )
    assert response.status_code == 201
    created = response.json()
    assert created["name"] == "Ada Lovelace"
    assert created["role"] == "member"

    admin = make_account("admin-list@vena-ia.dev", role="admin")
    listed = client.get("/users", headers=admin.headers)
    assert listed.status_code == 200
    assert len(listed.json()) == 2


def test_create_user_duplicate_email_conflicts(client) -> None:
    payload = {
        "name": "Grace Hopper",
        "email": "grace@vena-ia.dev",
        "password": TEST_PASSWORD,
    }
    first = client.post("/users", json=payload)
    second = client.post("/users", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409


def test_get_user_not_found_for_admin(client, make_account) -> None:
    admin = make_account("admin-missing@vena-ia.dev", role="admin")

    response = client.get("/users/does-not-exist", headers=admin.headers)

    assert response.status_code == 404


def test_user_can_read_own_profile_but_not_another_profile(client, make_account) -> None:
    owner = make_account("profile-owner@vena-ia.dev")
    other = make_account("profile-other@vena-ia.dev")

    own = client.get(f"/users/{owner.id}", headers=owner.headers)
    denied = client.get(f"/users/{other.id}", headers=owner.headers)

    assert own.status_code == 200
    assert denied.status_code == 404


def test_member_cannot_list_users(client, make_account) -> None:
    member = make_account("member-list@vena-ia.dev")

    response = client.get("/users", headers=member.headers)

    assert response.status_code == 403


def test_public_registration_rejects_role_and_role_update_is_unavailable(client) -> None:
    registered = client.post(
        "/users",
        json={
            "name": "Attacker",
            "email": "role-attack@vena-ia.dev",
            "password": TEST_PASSWORD,
            "role": "admin",
        },
    )

    assert registered.status_code == 422
