# ADR-0029 — Fronteira organizacional mínima para preparação de piloto controlado

**Status:** Aceita
**Data:** 2026-08-06
**Decisão relacionada:** `DEC-034`

## Contexto

A v1.9 precisa preparar ensaios sintéticos com dono, escopo e isolamento auditáveis,
sem transformar o monólito em uma plataforma empresarial, aceitar identidade do
cliente ou migrar automaticamente os recursos pessoais existentes para tenancy.

## Decisão

Adicionar ao Modular Monolith um módulo `organizations` com `Organization`, `Team`,
`Membership`, `PilotContext` e `PilotReadinessChecklist`. O usuário autenticado que
cria a organização recebe, na mesma transação, a única membership `OWNER` inicial.
`OWNER` e `ADMIN` são escopos organizacionais; `MEMBER` exige uma equipe. Índices
únicos parciais impedem memberships concorrentes duplicadas.

A autorização deriva exclusivamente de JWT válido, usuário persistido e membership
ativa consultada no banco. A sequência é usuário → membership → organização → papel
→ recurso. Acesso cross-organization e cross-team falha como `404`. Schemas de
entrada proíbem campos extras; `owner`, `role`, autoridade, status privilegiado,
`X-User-ID` e headers arbitrários nunca definem identidade ou autorização.

Os contratos públicos são `vena-ia.organization/v1`, `vena-ia.team/v1`,
`vena-ia.membership/v1`, `vena-ia.pilot-context/v1` e
`vena-ia.pilot-readiness-checklist/v1`. `READY_FOR_SYNTHETIC_REHEARSAL` exige
checklist completo, mas representa somente prontidão para revisão humana: não aprova
piloto real, deploy, produção, cliente ou CNC.

## Consequências

- Revogação de membership é aplicada na próxima autorização feita no banco; tokens
  continuam sujeitos às limitações de sessão registradas em R-013.
- Transferência de ownership, convites externos, billing, SSO/SCIM e domínio
  corporativo ficam fora do Package 1.
- Recursos pessoais existentes preservam seus contratos e ownership; não há
  reescrita ampla de tenancy.
- R-042 permanece crítico e monitorado, mesmo com cobertura fail-closed.
