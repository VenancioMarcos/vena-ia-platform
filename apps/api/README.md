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

## Endpoints Iniciais

* `GET /health`
* `GET /users`
* `GET /projects`
* `GET /files`
* `GET /chat`

