from unittest.mock import MagicMock

from app.main import app
from app.modules.documents.dependencies import get_knowledge_service


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


def test_failed_provider_persists_failed_question_without_fake_answer(
    client, make_account
) -> None:
    project_id, owner = _create_project(
        client,
        make_account,
        "chat-provider-failure@vena-ia.dev",
    )
    knowledge = MagicMock()
    knowledge.answer.side_effect = RuntimeError("provider offline")
    app.dependency_overrides[get_knowledge_service] = lambda: knowledge
    try:
        response = client.post(
            f"/chat/{project_id}/ask",
            headers=owner.headers,
            json={"question": "What does the document say?"},
        )
    finally:
        app.dependency_overrides.pop(get_knowledge_service, None)

    assert response.status_code == 502
    history = client.get(f"/chat/{project_id}/messages", headers=owner.headers)
    assert len(history.json()) == 1
    assert history.json()[0]["status"] == "FAILED"
    assert history.json()[0]["role"] == "user"
    assert history.json()[0]["error"] == "Serviço de IA indisponível; tente novamente."
