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

Os limites públicos de autenticação são configurados por
`AUTH_LOGIN_RATE_LIMIT_REQUESTS`, `AUTH_REGISTRATION_RATE_LIMIT_REQUESTS` e
`AUTH_RATE_LIMIT_WINDOW_SECONDS`. Ao excedê-los, a API retorna `429` com
`Retry-After`. O controle é local ao processo; produção horizontal ainda exige
um limitador distribuído ou gateway confiável.

O logout invalida o token apresentado no processo atual até sua expiração, além
de remover o cookie. Essa denylist é uma proteção intermediária: não persiste em
reinícios e deve ser distribuída antes de execução com múltiplas réplicas. Não
há renovação silenciosa de sessão.

## Endpoints

* `GET /health`
* `POST /auth/register`
* `POST /auth/login`
* `GET /auth/me`
* `POST /auth/logout`
* Rotas protegidas: `/users`, `/projects`, `/files`, `/documents`, `/chat`, `/ai`, `/cad`, `/manufacturing`, `/cnc` e `/research`
* `POST /documents/{document_id}/processing` — extrai texto de PDF e persiste chunks
* `GET /documents/{document_id}/chunks` — consulta chunks rastreáveis por documento/página
* `POST /documents/{document_id}/embeddings` — indexa chunks no pgvector
* `POST /projects/{project_id}/knowledge/search` — busca semântica rastreável
* `POST /projects/{project_id}/knowledge/ask` — resposta fundamentada em documentos
* `POST /cad/documents/{document_id}/analysis` — análise STEP preliminar autenticada
* `/research/articles` — biblioteca científica vinculada a projeto/documento
* `/research/articles/{id}/references` — referências preliminares auditáveis
* `/research/synthesis` — síntese RAG fundamentada com revisão humana
* `/research/doe/studies` — planos DOE preliminares
* `/research/anova/datasets` — preparação descritiva, sem inferência estatística
* `/research/reports` — relatórios em rascunho que exigem revisão do autor
* `POST /chat/{project_id}/ask` — RAG fundamentado com histórico persistente
* `GET /chat/{project_id}/messages` — histórico cronológico com fontes e estados

`GET /health` identifica a versão `1.1.0`.

Rotas protegidas aceitam cookie HttpOnly ou `Authorization: Bearer <token>`.
Consulte `docs/AUTHORIZATION_MATRIX.md`.

O processamento documental e a indexação da v0.5 são síncronos.
`RAG_CHUNK_SIZE` e `RAG_CHUNK_OVERLAP` configuram a fragmentação.
A análise CAD v0.6 aceita STEP Part 21 validado e retorna metadados e envelope
preliminar; não afirma volume, topologia ou propriedades de kernel geométrico.
