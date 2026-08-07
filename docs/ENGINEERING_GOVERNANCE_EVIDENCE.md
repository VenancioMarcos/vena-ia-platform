# Engineering Governance Evidence v1

## Contrato e endpoint

`GET /engineering/catalogs/{catalog_id}/governance` retorna
`vena-ia.engineering-governance-evidence/v1` somente depois da autorização do catálogo.
É read model efêmero, não ledger, aprovação, export comercial ou production readiness.

Inclui referência do catálogo, `scope_type`, Organization quando aplicável, provenance,
criação, lifecycle, classe de auditoria, retenção, exclusão, reconciliation, warnings,
limitations e revisão humana. Não expõe memberships, roles de terceiros, raw logs,
security internals, secrets ou tokens.

## Estados sustentados

| Scope | Lifecycle | Retention | Deletion | Reconciliation |
|---|---|---|---|---|
| `ORGANIZATION_OWNED` | `ACTIVE` | `RETAINED_FOR_TRACEABILITY_NO_TEMPORAL_POLICY` | `DELETE_NOT_EXPOSED` | `NOT_APPLICABLE` |
| `SYSTEM_REFERENCE` | `SYSTEM_READ_ONLY` | `SYSTEM_MANAGED_NO_TENANT_POLICY` | `SYSTEM_MUTATION_NOT_EXPOSED` | `SYSTEM_REFERENCE_NOT_RECONCILABLE` |
| `LEGACY_UNSCOPED` | Não exposto (`404`) | Bloqueado | Bloqueado | Sem endpoint; exige futura evidência humana controlada |

Não existe auto-assign, Organization default, update/delete/archive, retenção temporal
ou reconciliation pública. A FK `RESTRICT` impede cascade destrutivo.

## Auditoria, export e integridade

Criação organization-owned usa `ENGINEERING_CATALOG_CREATED` no audit existente. O
contrato referencia a classe do evento, mas avisa que o schema não prova ligação por
resource ID; não inventa correlação. Nenhum checksum é necessário para read model não
persistido. O GET individual é a única saída de metadata/evidence; bulk export não existe.

## Autorização e limites

Membership ativa lê o próprio catálogo; revoked/cross-org falha `404`. System reference
é legível por autenticado e nunca aparece como tenant-owned. Legacy não chega a
selection, recommendation, planning, workflow, assistance ou governance evidence.
Todos os resultados permanecem não produtivos e sob revisão humana; CNC não mudou.

## Release Candidate v2.1.0

Packages 1–2 são o escopo completo da v2.1; não existe Package 3. O contrato segue
v1, Alembic permanece `e61c4f8a2b90` e publicação depende do Owner Release Gate.
