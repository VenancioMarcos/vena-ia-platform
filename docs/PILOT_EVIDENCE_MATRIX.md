# Matriz de evidência do ensaio sintético v1.9

**Estado:** v1.9.0 publicada — revisão humana obrigatória; não produção

| Gate | Runbook existente | Evidence source/contract | Owner | Rollback | Falha / impacto em readiness |
|---|---|---|---|---|---|
| Onboarding | `docs/PILOT_GOVERNANCE.md` | `organization/v1`, `membership/v1` | Organization Owner | fechar contexto/revogar membership | ausente → `INCOMPLETE` |
| Authorization | `docs/AUTHORIZATION_MATRIX.md` | `membership/v1` | Security Owner | revogar membership | inválida/partial → bloqueia |
| Restore | `docs/runbooks/RECOVERY_DRILL.md` | `backup-set/v1` | Recovery Owner | restaurar somente ambiente descartável | ausente/failed → bloqueia |
| Incident | `docs/runbooks/INCIDENT_DRILL.md` | `incident-drill/v1` | Incident Owner | encerrar drill/preservar audit | ausente/failed → bloqueia |
| Observability | `docs/runbooks/OBSERVABILITY.md` | `metrics/v1` | Observability Owner | limpar evidência temporária | partial → `INCOMPLETE` |
| Resilience | `docs/runbooks/DEPENDENCY_DEGRADATION.md` | `resilience-policy/v1` | Reliability Owner | retornar modo normal descartável | failed → `REHEARSAL_FAILED` |
| Capacity | `docs/runbooks/CONTROLLED_CAPACITY.md` | `capacity-evidence/v1` | Capacity Owner | encerrar carga sintética | nunca extrapolar para produção |
| Privacy | `docs/PILOT_GOVERNANCE.md` | `pilot-readiness-checklist/v1` | Privacy Reviewer | excluir fixture permitida | qualquer false → bloqueia |
| Support | `docs/runbooks/INCIDENT_DRILL.md` | `pilot-evidence/v1` | Support Owner | escalar ao CTO sem notificação externa | gap → `NOT_AVAILABLE` |
| Rollback | `docs/PILOT_GOVERNANCE.md` | `pilot-rollback/v1` | Organization Owner | resultado por ação | `FAILED` bloqueia; mistura → `PARTIAL` |
| CNC virtual | `docs/PERMANENT_OPERATIONAL_LIMITS.md` | `virtual-cnc-plan-validation/v1` | Engineering Reviewer | descartar payload em memória | rejeição → sem readiness |

`AVAILABLE`, `PARTIAL`, `NOT_AVAILABLE`, `FAILED` e `NOT_APPLICABLE` são estados
fechados. SHA-256 compara o payload canônico: detecta alteração, mas não prova
identidade, autoria, não repúdio, assinatura digital ou confiança externa.
