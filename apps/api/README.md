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
* `POST /documents/{document_id}/processing` — extrai texto de PDF e persiste chunks
* `GET /documents/{document_id}/chunks` — consulta chunks rastreáveis por documento/página

Rotas protegidas aceitam cookie HttpOnly ou `Authorization: Bearer <token>`.
Consulte `docs/AUTHORIZATION_MATRIX.md`.

O processamento documental da v0.5 é síncrono e limitado a PDFs com texto
extraível. `RAG_CHUNK_SIZE` e `RAG_CHUNK_OVERLAP` configuram a fragmentação.
OCR, embeddings, busca vetorial e respostas com LLM permanecem fora desta entrega.
