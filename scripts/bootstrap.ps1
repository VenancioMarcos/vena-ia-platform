$ErrorActionPreference = "Stop"

Write-Host "Vena_IA bootstrap"

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env from .env.example"
}

Write-Host "Next steps:"
Write-Host "1. docker compose up postgres redis minio"
Write-Host "2. cd apps/api; python -m venv .venv; .\\.venv\\Scripts\\Activate.ps1; pip install -e '.[dev]'; uvicorn app.main:app --reload"
Write-Host "3. cd apps/web; npm install; npm run dev"

