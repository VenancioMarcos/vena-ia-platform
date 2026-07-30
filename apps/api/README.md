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
* Rotas protegidas: `/users`, `/projects`, `/files`, `/documents`, `/chat`, `/ai` e `/cad`
* `POST /documents/{document_id}/processing` — extrai texto de PDF e persiste chunks
* `GET /documents/{document_id}/chunks` — consulta chunks rastreáveis por documento/página
* `POST /documents/{document_id}/embeddings` — indexa chunks no pgvector
* `POST /projects/{project_id}/knowledge/search` — busca semântica rastreável
* `POST /projects/{project_id}/knowledge/ask` — resposta fundamentada em documentos
* `POST /cad/documents/{document_id}/analysis` — análise STEP preliminar autenticada

Rotas protegidas aceitam cookie HttpOnly ou `Authorization: Bearer <token>`.
Consulte `docs/AUTHORIZATION_MATRIX.md`.

O processamento documental e a indexação da v0.5 são síncronos.
`RAG_CHUNK_SIZE` e `RAG_CHUNK_OVERLAP` configuram a fragmentação.
A análise CAD v0.6 aceita STEP Part 21 validado e retorna metadados e envelope
preliminar; não afirma volume, topologia ou propriedades de kernel geométrico.
