# Vena_IA Platform v2.1.0 — Enterprise Engineering Governance

## Release Candidate

A v2.1.0 introduz ownership por Organization nos catálogos Engineering e evidence
de governança read-only. Estas notas descrevem uma candidata ainda não publicada:
não existe tag, GitHub Release ou deploy.

## Ownership e compatibilidade

- `ORGANIZATION_OWNED` exige membership ativa; OWNER/ADMIN escrevem e membership
  autorizada lê; cross-org retorna `404`.
- `SYSTEM_REFERENCE` não possui tenant owner, é read-only e preserva provenance.
- Dados anteriores são `LEGACY_UNSCOPED`: invisíveis, não selecionáveis, não
  exportáveis e nunca atribuídos automaticamente a uma Organization.
- Migration `e61c4f8a2b90` preserva legados sem owner inventado, usa FK `RESTRICT`,
  unicidade por Organization e downgrade data-preserving.
- Contratos Engineering v1 permanecem versionados; campos de scope são aditivos e
  a Organization na criação é a quebra mínima documentada para remover escrita global.

## Governance evidence

`GET /engineering/catalogs/{catalog_id}/governance` retorna
`vena-ia.engineering-governance-evidence/v1` após autorização. O read model é efêmero,
sem ledger, persistence, bulk export, membership disclosure, raw logs ou secrets.
Lifecycle, audit event class, retention, deletion e reconciliation refletem somente
capacidades reais. Não há delete/archive/reconciliation pública ou retenção temporal.

## Compatibilidade downstream e segurança

Selection, recommendation, review report, planning, integrated workflow e specialized
assistance reutilizam a fronteira fail-closed. Membership revogada perde acesso e
body/header/browser não concede authority: `TOKEN + DATABASE = AUTHORITY`.

R-042 permanece residual. R-048 está somente `MITIGADO PARCIALMENTE / MONITORAR`.
R-044–R-047 permanecem residuais; R-049 e R-050 são gates futuros de v2.2/v3.0.

## Evidência de validação

- Alembic single head e ciclo PostgreSQL upgrade/downgrade/upgrade;
- Ruff, mypy e pytest integral;
- testes OWNER/ADMIN/MEMBER, cross-org, revogação, system/legacy e downstream;
- OpenAPI, secret scan, Compose e CI de backend/frontend aplicáveis.

No gate local final: Ruff e mypy (168 arquivos) passaram; API registrou `357 passed,
2 skipped`; operations, `69 passed, 7 skipped`; focais de versão/governança, `70
passed`; OpenAPI `2.1.0` possui 79 paths; Alembic mantém o head `e61c4f8a2b90`;
Compose, secret scan e diff/check passaram. Backend e Frontend CI no HEAD final são a
evidência oficial dos serviços PostgreSQL e do runtime Node 22.20/pnpm 11.9.

## Limites absolutos

Enterprise governance não significa production readiness. Tudo permanece
`NON_PRODUCTION` e `REQUIRES_HUMAN_REVIEW`. Não há toolpath, postprocessor, G-code,
M-code, NC/DNC, transmissão, machine control, piloto real, publicação comercial ou
deploy. Publicação depende de autorização direta do proprietário.
