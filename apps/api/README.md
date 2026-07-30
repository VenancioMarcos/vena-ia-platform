# Vena_IA API

Backend principal da Vena_IA Platform.

## Stack

* Python 3.13
* FastAPI
* Pydantic v2
* SQLAlchemy
* Alembic

## Desenvolvimento

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

Defina `AUTH_SECRET_KEY` com um segredo aleatório de pelo menos 32 bytes antes de
usar login fora dos testes.

## Endpoints

* `GET /health`
* `POST /auth/register`
* `POST /auth/login`
* `GET /auth/me`
* `POST /auth/logout`
* Rotas protegidas: `/users`, `/projects`, `/files`, `/documents`, `/chat` e `/ai`

Rotas protegidas aceitam cookie HttpOnly ou `Authorization: Bearer <token>`.
Consulte `docs/AUTHORIZATION_MATRIX.md`.
