# Estado de execução CTO

```text
MISSION=TASK_V12_003
STATE=V1_2_PACKAGE_3_VALIDATION
BRANCH=codex/v1.2-auth-rate-limiting
START_HEAD=47102286cfe1f6f977b69693da943337118399a7
V1_1_RELEASE=https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.1.0
ROADMAP_RANGE=v1.2_TO_v2.0
V1_2_PACKAGE_1=APPROVED_BY_CTO
V1_2_PACKAGE_2=SESSION_INVALIDATION_AND_AUTH_ROBUSTNESS
V1_2_PACKAGE_3=LEGACY_CREDENTIAL_AND_SECURITY_AUDIT
BLOCKERS=NONE
SOURCE_REVIEW=PROJECT_CONTEXT_CHANGELOG_ROADMAP_DECISIONS_GOVERNANCE_ARCHITECTURE_ADRS_RISKS_LIMITS_CTO_COMPLETE
DECISIONS_ROOT=MISSING_OFFICIAL_EQUIVALENT_docs/DECISIONS.md_USED
ROADMAP_PR=https://github.com/VenancioMarcos/vena-ia-platform/pull/12
ROADMAP_MERGE=6e1065d3df78b27d01a16009579af3c7fa8c961e
V1_2_PR=https://github.com/VenancioMarcos/vena-ia-platform/pull/13
LOCAL_GATES=RUFF_MYPY_PYTEST_182_PASS
GITHUB_CHECKS=PACKAGE_3_PENDING
PACKAGE_2_HEAD=90138c3bde37f4196626942bbce3e375d3dcbda7
NEXT=POSTGRES_DOCKER_OPENAPI_FRONTEND_COMMIT_PUSH_CI
```

Este arquivo deve ser atualizado apenas com evidências verificadas.

## Registro de Entrega

### Objetivo

Consolidar o roadmap oficial entre v1.2 e v2.0 por gates verificáveis e iniciar
o primeiro pacote de segurança da v1.2 após integrar a documentação.

### Escopo entregue

* diagnóstico de capacidades concluídas, parciais e ausentes;
* sequência v1.2–v2.0 por segurança, recuperação, observação, confiabilidade
  e evolução de engenharia já prevista;
* primeiro pacote v1.2 limitado a rate limiting de cadastro/login;
* janela fixa local e configurável, `429`/`Retry-After`, chave por conexão e
  proteção compartilhada das duas rotas de cadastro, sem `X-User-ID`.

### Arquivos modificados

* roadmaps executivo e detalhado;
* changelog, contexto, decisões, riscos e controles CTO.

### Testes realizados

Validação documental, links/formatos, diff e secret scan; CI conforme paths da PR.

### Critérios de aceitação

Roadmap integrado sem histórico apagado; primeiro pacote v1.2 em Draft PR com
testes e CI aprovados; nenhuma v1.3 ou ação proibida iniciada.

### Próximo passo

Revisão do CTO na Draft PR #13; nenhuma ação posterior foi iniciada.
