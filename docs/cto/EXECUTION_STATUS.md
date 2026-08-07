# Estado de execução CTO

```text
CONTINUOUS_CTO_CODEX_FLOW_POLICY=ACTIVE
FLOW_RECOVERY_APPLIED=TRUE
LAST_TERMINAL_TASK=TASK-V18-002
LAST_TERMINAL_HEAD=54f353c9b7cd04245e404cabf8c7adf220593d49
OPERATIONAL_STATE=AWAITING_CTO_NEXT_ORDER
FLOW_TERMINATION_WITHOUT_EXPLICIT_ORDER=PROHIBITED
STATUS_BEFORE_WAITING=MANDATORY
NEXT_ORDER_CAPTURE=MANDATORY
```

TASK-V17-003: relatório versionado, conclusão segura, checklist, incerteza,
ausências e rastreabilidade implementados; validação terminal em andamento.

```text
MISSION=TASK_V17_002
STATE=V1_7_PACKAGE_2_VALIDATION_IN_PROGRESS
BRANCH=codex/v1.7-intelligent-engineering
START_HEAD=4fc524197eadc1fe30982d4102c235c2c10090e9
PULL_REQUEST=18
```

Contrato v1, operações allowlisted, compatibilidade, parâmetros, tempo/custo,
fontes, unidades e revisão humana implementados. Gate terminal em execução.

```text
MISSION=TASK_V16_003_R1
STATE=V1_6_PACKAGE_3_REMEDIATION_IN_PROGRESS
BRANCH=codex/v1.6-reliability-scalability
START_HEAD=310b85d389c76f043e6b7cd8aa60cd68e6315849
V1_1_RELEASE=https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.1.0
ROADMAP_RANGE=v1.2_TO_v2.0
V1_2_PACKAGE_1=APPROVED_BY_CTO
V1_2_PACKAGE_2=SESSION_INVALIDATION_AND_AUTH_ROBUSTNESS
V1_2_PACKAGE_3=APPROVED_BY_CTO
V1_2_PACKAGE_4=DISTRIBUTED_AUTHENTICATION_CONTROLS
BLOCKERS=NONE
V1_6_PACKAGE_3_START_HEAD=fef319b0eff0cebc2d27060488d28d828b73cceb
V1_6_CAPACITY_PROFILE=vena-ia.capacity-profile/v1
V1_6_CAPACITY_EVIDENCE=vena-ia.capacity-evidence/v1
V1_6_PREVIOUS_EVIDENCE=HARNESS_ONLY_BASELINE
V1_6_TOPOLOGY=2_API_PROCESSES_2_WORKER_PROCESSES_SHARED_POSTGRESQL_REDIS_MINIO
V1_6_CONTROLLED_LOAD=REAL_HTTP_CROSS_INSTANCE_BOUNDED
V1_6_SHORT_SOAK=30_SECONDS_INTEGRATED_CLEANUP_REQUIRED
V1_6_CAPACITY_LIMIT=TECHNICAL_TEST_GUARDRAIL_NOT_SLO_SLA_PRODUCTION
V1_6_PACKAGE_3_CODE_HEAD=500c94f
V1_6_PACKAGE_3_LOCAL=3_POLICIES_RUFF_MYPY_140_266_API_2_SKIP_65_OPERATIONAL_6_SKIP_FRONTEND_COMPOSE_ALEMBIC_PASS
V1_6_PACKAGE_3_CI=BACKEND_31060952153_FRONTEND_31060952144_RUNTIME_31060952139_CAPACITY_31060952197_SUCCESS
V1_6_PACKAGE_3_CI_TESTS=268_API_71_OPERATIONAL_10_CAPACITY_1_E2E_POSTGRESQL_REDIS_MINIO_PASS
V1_6_PACKAGE_3_ARTIFACT=8952091174_SHA256_5245b0f6566606ef3345cc8bf6a9a829f30563787a503c3f1954b6a6c11e3414
V1_6_PACKAGE_3_PR_STATE=DRAFT_MERGEABLE_R1_CI_PENDING
V1_6_PACKAGE_2_START_HEAD=2f5d427d6cecd4094cc96754c80d98954b1187c0
V1_6_RESILIENCE_POLICY=vena-ia.resilience-policy/v1
V1_6_RESILIENCE=DEADLINE_RETRY_BACKOFF_JITTER_FAILURE_CLASSES_BACKPRESSURE
V1_6_DEPENDENCIES=POSTGRESQL_REDIS_MINIO_OPENAI_WORKER_BACKUP
V1_6_RESILIENCE_DRILL=20_SYNTHETIC_SCENARIOS_NO_EXTERNAL_AI
V1_6_PACKAGE_2_MIGRATION_HEAD=b18e4c7d2a91_UNCHANGED
V1_6_PACKAGE_2_LIMITS=NO_CAPACITY_SLO_SLA_MERGE_RELEASE_DEPLOY
V1_6_PACKAGE_2_CODE_HEAD=1905884359d2e298c6d2f3f6113586e47c1c69fb
V1_6_PACKAGE_2_LOCAL=POLICIES_RUFF_MYPY_138_266_API_PASS_2_SKIP_55_OPERATIONAL_PASS_6_SKIP_FRONTEND_COMPOSE_ALEMBIC_PASS
V1_6_PACKAGE_2_CI=BACKEND_31059513786_FRONTEND_31059513849_RUNTIME_POLICY_31059513794_SUCCESS
V1_6_PACKAGE_2_CI_TESTS=268_API_61_OPERATIONAL_POSTGRESQL_REDIS_MINIO_API_WEB_IMAGES_PASS
V1_6_PACKAGE_2_PR_STATE=DRAFT_MERGEABLE_CI_GREEN
V1_6_PACKAGE_1_START_HEAD=f6b63992d9d0ac5e5d29656e092eba1b364ff55a
V1_6_RUNTIME_POLICY=vena-ia.runtime-policy/v1
V1_6_PYTHON=3.13.11_OFFICIAL_3.14.6_EXPERIMENTAL
V1_6_NODE=22.20.0
V1_6_PNPM=11.9.0
V1_6_IMAGES=TAG_AND_MULTIARCH_DIGEST_PINNED
V1_6_MIGRATION_HEAD=b18e4c7d2a91_UNCHANGED
V1_6_DEPLOY=PROHIBITED
V1_6_LOCAL=POLICY_PASS_RUFF_MYPY_251_API_PASS_2_SKIP_49_OPERATIONAL_PASS_6_SKIP_FRONTEND_PASS_COMPOSE_PASS
V1_6_PYTHON_314_CLEAN=INSTALL_IMPORTS_RUFF_MYPY_251_API_PASS_2_SKIP_49_OPERATIONAL_PASS_6_SKIP
V1_6_LOCAL_DOCKER=DAEMON_ABSENT_BUILDS_REQUIRED_IN_CI
V1_6_PR=https://github.com/VenancioMarcos/vena-ia-platform/pull/17
V1_6_FINAL_CODE_HEAD=84c219a8b94a4b0865dcd00860c68230159f5a27
V1_6_CI=BACKEND_31057602795_FRONTEND_31057602796_RUNTIME_POLICY_31057602808_SUCCESS
V1_6_CI_TESTS=RUFF_MYPY_135_ALEMBIC_CYCLE_253_API_55_OPERATIONAL_FRONTEND_API_WEB_IMAGES_PASS
V1_6_PR_STATE=DRAFT_MERGEABLE_CI_GREEN
V1_5_RELEASE_START_HEAD=bd4908b54e5169d4e0c373cee1d6a70fe2e7bd67
V1_5_RELEASE_VERSION=1.5.0
V1_5_RELEASE_MIGRATION_HEAD=b18e4c7d2a91
V1_5_RELEASE_DEPLOY=PROHIBITED
V1_5_RELEASE_PREMERGE_LOCAL=RUFF_MYPY_251_API_PASS_2_SKIP_46_OPERATIONAL_PASS_6_SKIP_40_FOCAL_PASS_1_SKIP_FRONTEND_TYPECHECK_BUILD_COMPOSE_OPENAPI_55
V1_5_RELEASE_LOCAL_DOCKER=DAEMON_ABSENT_REAL_POSTGRESQL_REDIS_MINIO_EVIDENCE_FROM_FINAL_CI
V1_5_PR_STATE=MERGED
V1_5_MERGE_COMMIT=a3c2f6befa11cdfe8a8678a6cc9212ea17a975be
V1_5_RELEASE_COMMIT=THIS_RELEASE_RECORD_COMMIT
V1_5_TAG=v1.5.0
V1_5_TAG_TARGET=V1_5_RELEASE_COMMIT
V1_5_RELEASE=https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.5.0
V1_5_RELEASE_CI=BACKEND_31053239113_FRONTEND_31053244413_SUCCESS
V1_5_POSTMERGE=RUFF_MYPY_251_API_PASS_2_SKIP_46_OPERATIONAL_PASS_6_SKIP_FRONTEND_TYPECHECK_BUILD_COMPOSE_OPENAPI_55
V1_5_DEPLOY=NOT_PERFORMED
NEXT=CTO_REVIEW
V1_5_PACKAGE_2_START_HEAD=fe7d53211b1b6a103e0d05968d46698013cdaf21
V1_5_PACKAGE_2_CODE_HEAD=a2662f8
V1_5_PACKAGE_2_RECOVERY=POSTGRESQL_SOURCE_REDIS_RECONCILIATION_ATOMIC_CAS
V1_5_PACKAGE_2_OCR=CLASS_B_DEFERRED_NO_IMPLEMENTATION
V1_5_PACKAGE_2_LOCAL=RUFF_MYPY_251_API_PASS_2_SKIP_46_OPERATIONAL_PASS_6_SKIP_FRONTEND_COMPOSE_OPENAPI_55
V1_5_PACKAGE_2_PERFORMANCE=2000_OPS_21.4MS_AVG_0.010385MS_P50_0.0032MS_P95_0.0293MS_P99_0.0445MS_SYNTHETIC_ONLY
V1_5_PACKAGE_2_LOCAL_DOCKER=DAEMON_ABSENT_REAL_POSTGRESQL_REDIS_MINIO_REQUIRED_IN_CI
V1_5_PACKAGE_2_CI=RUFF_MYPY_ALEMBIC_253_API_PASS_52_OPERATIONAL_PASS_POSTGRESQL_REDIS_MINIO_FRONTEND_PASS
V1_5_PACKAGE_2_CI_RUN=https://github.com/VenancioMarcos/vena-ia-platform/actions/runs/31051848806
V1_5_PACKAGE_2_FRONTEND_CI_RUN=https://github.com/VenancioMarcos/vena-ia-platform/actions/runs/31051848820
V1_5_PACKAGE_2_RECOVERY_METRICS=OBJECTS_1_BYTES_27_BACKUP_0.425S_RESTORE_0.408S_RPO_1.382S_NON_PRODUCTION
SOURCE_REVIEW=PROJECT_CONTEXT_CHANGELOG_ROADMAP_DECISIONS_GOVERNANCE_ARCHITECTURE_ADRS_RISKS_LIMITS_CTO_COMPLETE
DECISIONS_ROOT=MISSING_OFFICIAL_EQUIVALENT_docs/DECISIONS.md_USED
ROADMAP_PR=https://github.com/VenancioMarcos/vena-ia-platform/pull/12
ROADMAP_MERGE=6e1065d3df78b27d01a16009579af3c7fa8c961e
V1_2_PR=https://github.com/VenancioMarcos/vena-ia-platform/pull/13
V1_2_MERGE=0e386802be6af5c45a66bf8c6e622ac62119a8f2
V1_2_RELEASE_COMMIT=663dbc2da7536382ff796f916bd105118a3a5938
V1_2_TAG=v1.2.0
V1_2_RELEASE=https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.2.0
V1_3_PR=https://github.com/VenancioMarcos/vena-ia-platform/pull/14
V1_3_MERGE=24c19191af576c7db9acd1fc0df9f1e352ff62a4
V1_3_POST_MERGE=RUFF_MYPY_232_PASS_FRONTEND_COMPOSE_OPENAPI_1.3.0_ALEMBIC_PASS
V1_3_RELEASE_COMMIT=e075657dbbd4500e95acbe5e927443710b0dc9d0
V1_3_TAG=v1.3.0
V1_3_TAG_TARGET=e075657dbbd4500e95acbe5e927443710b0dc9d0
V1_3_RELEASE=https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.3.0
V1_3_TAG_VALIDATION=HEALTH_RUNTIME_OPENAPI_49_PATHS_40_PASS_4_LOCAL_INTEGRATION_SKIP
V1_4_PR=https://github.com/VenancioMarcos/vena-ia-platform/pull/15
V1_4_MERGE=13801560af0ff2bb05c0ad02a5ccf3c5cf35b111
V1_4_TAG=v1.4.0
V1_4_RELEASE=https://github.com/VenancioMarcos/vena-ia-platform/releases/tag/v1.4.0
V1_5_PR=https://github.com/VenancioMarcos/vena-ia-platform/pull/16
V1_5_PACKAGE_1_CODE_HEAD=6b6f871
V1_5_PACKAGE_1_CONTRACT=vena-ia.job/v1
V1_5_PACKAGE_1_MIGRATION=b18e4c7d2a91
V1_5_PACKAGE_1_LOCAL=RUFF_MYPY_236_API_PASS_2_SKIP_46_OPERATIONAL_PASS_6_SKIP_FRONTEND_COMPOSE_OPENAPI_55
V1_5_PACKAGE_1_LOCAL_DOCKER=DAEMON_UNAVAILABLE_REAL_POSTGRESQL_REDIS_MINIO_DEFERRED_TO_CI
V1_5_PACKAGE_1_CI=RUFF_MYPY_ALEMBIC_238_API_PASS_52_OPERATIONAL_PASS_POSTGRESQL_REDIS_MINIO_FRONTEND_PASS
V1_5_PACKAGE_1_CI_RUN=https://github.com/VenancioMarcos/vena-ia-platform/actions/runs/31047601246
V1_4_PACKAGE_1_CODE_HEAD=b4fbde7
V1_4_LOCAL=RUFF_MYPY_240_PASS_6_CONDITIONAL_SKIP_FRONTEND_COMPOSE_OPENAPI_50
V1_4_CI=202_API_PASS_44_OPERATIONAL_PASS_POSTGRESQL_REDIS_MINIO_READY
V1_4_CI_RUN=https://github.com/VenancioMarcos/vena-ia-platform/actions/runs/30746888256
V1_4_PACKAGE_2_CODE_HEAD=2ce8f54
V1_4_PACKAGE_2_LOCAL=RUFF_MYPY_213_PASS_1_SKIP_41_OPERATIONAL_PASS_5_CONDITIONAL_SKIP_FRONTEND_COMPOSE_OPENAPI_51_SECRET_SCAN_PASS
V1_4_PACKAGE_2_PERFORMANCE=100_HEALTH_REQUESTS_AVERAGE_9.638MS_WITH_LOCAL_TRACING_NON_PRODUCTION
V1_4_PACKAGE_2_MIGRATION=a63d2f8c1b04
V1_4_PACKAGE_2_LOCAL_DOCKER=DAEMON_TIMEOUT_POSTGRESQL_REDIS_MINIO_REAL_VALIDATION_DEFERRED_TO_CI
V1_4_PACKAGE_2_INITIAL_CI=RUFF_MYPY_MIGRATIONS_214_API_PASS_2_OPERATIONAL_FAIL_STALE_HEAD_ASSERTION
V1_4_PACKAGE_2_ALEMBIC_FIX=DERIVED_SINGLE_OFFICIAL_HEAD_MANIFEST_EQUALS_OFFICIAL_RESTORE_EQUALS_MANIFEST
V1_4_PACKAGE_2_VALIDATED_HEAD=d588ece19eb080ec14ef604c2346134d496f307d
V1_4_PACKAGE_2_FINAL_CI=RUFF_MYPY_ALEMBIC_UP_DOWN_UP_214_API_PASS_46_OPERATIONAL_PASS_POSTGRESQL_REDIS_MINIO
V1_4_PACKAGE_2_FINAL_CI_RUN=https://github.com/VenancioMarcos/vena-ia-platform/actions/runs/30964923110
V1_4_PACKAGE_2_RECOVERY_METRICS=OBJECTS_1_BYTES_27_BACKUP_0.397S_RESTORE_0.404S_RPO_1.248S_NON_PRODUCTION
V1_4_PACKAGE_3_CODE_HEAD=2f784c6
V1_4_PACKAGE_3_CONTRACT=vena-ia.incident-drill/v1
V1_4_PACKAGE_3_SCENARIOS=11_CONTROLLED_WITH_POSTGRESQL_REDIS_MINIO_RECOVERY
V1_4_PACKAGE_3_BUNDLE=DETERMINISTIC_JSON_SHA256_OUTSIDE_REPOSITORY_FAIL_CLOSED
V1_4_PACKAGE_3_THRESHOLDS=BOUNDED_SYNTHETIC_NO_USER_MONITORING
V1_4_PACKAGE_3_RETENTION=AUDIT_POSTGRESQL_90_DAYS_METRICS_TRACING_EPHEMERAL
V1_4_PACKAGE_3_EXTERNAL_BACKEND=DEFERRED_FUTURE_GATE
V1_4_PACKAGE_3_ALERT_DELIVERY=NOOP_LOCAL_ONLY
V1_4_PACKAGE_3_LOCAL=RUFF_MYPY_215_API_PASS_1_SKIP_46_OPERATIONAL_PASS_6_SKIP_FRONTEND_COMPOSE_OPENAPI_51_SECRET_SCAN_PASS
V1_4_PACKAGE_3_PERFORMANCE=100_DRILLS_TOTAL_151.973MS_AVG_1.520MS_P50_1.335MS_P95_2.206MS_P99_2.577MS_SYNTHETIC_NON_PRODUCTION
V1_4_PACKAGE_3_LOCAL_DOCKER=DAEMON_UNAVAILABLE_REAL_POSTGRESQL_REDIS_MINIO_DEFERRED_TO_CI
V1_4_PACKAGE_3_RISKS=R010_MITIGATED_R032_PARTIAL_MONITOR_R033_PARTIAL_MONITOR
V1_4_PACKAGE_3_VALIDATED_HEAD=22f224b87cda062033d2469c0016eaa5698f2957
V1_4_PACKAGE_3_FINAL_CI=RUFF_MYPY_ALEMBIC_UP_DOWN_UP_216_API_PASS_52_OPERATIONAL_PASS_POSTGRESQL_REDIS_MINIO
V1_4_PACKAGE_3_FINAL_CI_RUN=https://github.com/VenancioMarcos/vena-ia-platform/actions/runs/30967191649
V1_4_PACKAGE_3_RECOVERY_METRICS=OBJECTS_1_BYTES_27_BACKUP_0.426S_RESTORE_0.418S_RPO_1.247S_NON_PRODUCTION
V1_3_PACKAGE_1_HEAD=20416e7df7b4f509a63065eb2251da804330ae94
V1_3_PACKAGE_2_CODE_HEAD=eb5b192
V1_3_LOCAL_GATES=RUFF_MYPY_PYTEST_215_PASS_FRONTEND_PASS_COMPOSE_PASS
V1_3_CI=POSTGRESQL_MINIO_COMBINED_BACKUP_RESTORE_ROUND_TRIP_PASS
V1_3_CI_RUN=https://github.com/VenancioMarcos/vena-ia-platform/actions/runs/30744271224
V1_3_PACKAGE_3_CODE_HEAD=fc0fb73
V1_3_PACKAGE_3_DOCS_HEAD=0b1755d
V1_3_PACKAGE_3_LOCAL=RUFF_MYPY_232_PASS_5_CONDITIONAL_SKIP_FRONTEND_COMPOSE_PASS
V1_3_PACKAGE_3_CI=194_API_PASS_43_OPERATIONAL_PASS
V1_3_PACKAGE_3_CI_RUN=https://github.com/VenancioMarcos/vena-ia-platform/actions/runs/30745399876
V1_3_RECOVERY_METRICS=OBJECTS_1_BYTES_27_BACKUP_0.409S_RESTORE_0.415S_RPO_1.262S_NON_PRODUCTION
LOCAL_GATES=RUFF_MYPY_PYTEST_190_REDIS_INTEGRATION_FRONTEND_DOCKER_CONFIG_PASS
DOCKER_IMAGE_BUILD=API_COMPILED_EXPORT_FAILED_DOCKER_DAEMON_500_WEB_PENDING_CI
GITHUB_CHECKS=PACKAGE_4_BACKEND_AND_FRONTEND_CI_PASS
PACKAGE_4_CODE_HEAD=f7e83ada4ea6984b2cee93a79ced327c0a7ac36a
PACKAGE_3_HEAD=eae12bf3e1616cef88f994b99fcd629f682cfbec
PACKAGE_2_HEAD=90138c3bde37f4196626942bbce3e375d3dcbda7
NEXT=CTO_REVIEW
```

Este arquivo deve ser atualizado apenas com evidências verificadas.

## Registro de Entrega

### Objetivo

Distribuir os controles de rate limiting e revogação de autenticação usando a
infraestrutura Redis existente, com falha fechada e auditoria.

### Escopo entregue

* cota atômica compartilhada por Redis para login e aliases de cadastro;
* revogação distribuída com fingerprint derivado e TTL do JWT;
* falha fechada `503` em limite, consulta e escrita de revogação;
* modo em memória explícito e proibido em produção;
* integração Redis real e CI com serviço Redis.

### Arquivos modificados

* backend de autenticação, configuração, dependência e testes;
* workflow de Backend CI;
* changelog, contexto, segurança, roadmap, decisões, riscos, ADR e controles CTO.

### Testes realizados

Ruff e mypy aprovados; 190 testes incluindo Redis real; frontend typecheck/build;
Docker Compose válido. O build API compilou integralmente, mas o daemon Docker
local falhou na exportação com EOF/500 e ficou indisponível. Backend CI com
PostgreSQL e Redis e Frontend CI/build concluíram com sucesso.

### Critérios de aceitação

Estado distribuído entre instâncias, TTL correto, chaves sem segredo/PII,
indisponibilidade sem bypass e contratos/autorização preservados.

### Próximo passo

Revisão do CTO na Draft PR #13; nenhuma ação posterior foi iniciada.

## 2026-08-06 — TASK-V18-003 Package 3 local terminal

`FeatureRecognizer` rule `1.0.0` consome a mesma shape OCCT do adapter e expõe
`vena-ia.geometry-features/v1`. O corpus sintético aprovou primitivas planares e
cilíndricas, um e dois furos passantes, rejeição de cilindro externo/furo cego,
topologia inválida, malformed e determinismo. Closed hole e slot foram adiados.
Ruff, mypy em 151 arquivos e pytest integral (`358 passed, 9 skipped`) passaram;
OpenAPI 3.1.0 mantém 60 paths. Não houve migration, merge, tag, Release ou deploy.

## 2026-08-06 — TASK-V18-004 Package 4 local terminal

`FeaturePlanningBridge` rule `1.0.0` expõe `vena-ia.feature-planning/v1` em rota
autenticada. Through hole produz somente `DRILLING_CANDIDATE` não executável;
primitivas e contextos ambíguos não geram candidate. Três catálogos explícitos
reutilizam a recommendation v1.7; ausências permanecem `REQUIRED_INPUT`.
Ruff, mypy em 152 arquivos e pytest integral (`370 passed, 9 skipped`) passaram;
OpenAPI 3.1.0 possui 61 paths. O gate de roadmap está `SATISFIED` sem CAM,
toolpath, G-code, merge, tag, Release ou deploy.

## 2026-08-06 — TASK-V18-005 release candidate local gate

Versões API/FastAPI/health/OpenAPI e frontend foram alinhadas em `1.8.0`; migration
head permanece `c27f6d9e4a10`. Corpus CAD/features/planning focal aprovou 54 testes.
Ruff, mypy em 152 arquivos e regressão integral (`370 passed, 9 skipped`) passaram.
Frontend typecheck/build, runtime policy, Compose config e secret scan passaram.
O wrapper pnpm local estava em Node 24/pnpm 11.16 e tentou registry; os scripts
instalados passaram diretamente, enquanto Node 22.20/pnpm 11.9 permanece gate do CI.
PR #19 continua Draft; merge, tag, Release, deploy e v1.9 não estão autorizados.

## 2026-08-06 — Release v1.8.0 authorized finalization

O proprietário autorizou diretamente retirar Draft, Squash Merge, tag e GitHub
Release. A PR #19 foi integrada em `a066c1c`; a árvore da main é idêntica ao RC
validado. O gate pós-merge aprovou 43 testes focais, Alembic `c27f6d9e4a10`, runtime
policy e Compose. A tag/Release `v1.8.0` são publicadas sem deploy; v1.9 somente pode
iniciar no Package 1 oficial após consulta a ROADMAP/DECISIONS.

## 2026-08-06 — TASK-V19-000 decomposition

Main `997f0ba`, tag/Release v1.8.0 e Working Tree limpa foram confirmadas; não
existia branch/PR v1.9. A documentação oficial não possuía Packages. A proposta
mínima registra Package 1 de governança/organização e Package 2 de ensaio
operacional/validação virtual; Package 3 não é necessário. DEC-034 permanece
proposta para aprovação do CTO e R-042 registra isolamento organizacional crítico.
Nenhuma implementação, migration, deploy, piloto real ou saída CNC foi iniciada.

## 2026-08-06 — TASK-V19-001 aprovação

O CTO aprovou DEC-034 e tornou a decomposição em dois Packages a baseline oficial.
Package 1 está `APPROVED_FOR_IMPLEMENTATION`; Package 2 permanece `NOT_STARTED`.
R-042 continua CRÍTICO e ABERTO/GATE, sem redução decorrente da aprovação documental.

## 2026-08-06 — TASK-V19-001 Package 1

A PR documental #20 foi integrada em `3776fc4`. Na branch funcional, o Package 1
implementa Organization/Team/Membership, papéis allowlisted, bootstrap owner,
revogação, Pilot Context, readiness/privacy e auditoria existente. A migration única
avança o head para `d39a7b2c5e11`. O gate local aprovou Ruff, mypy (161 arquivos),
314 testes da API (2 skips), 13 testes focais novos, 12 testes operacionais,
frontend typecheck/build, runtime policy, Compose config e OpenAPI 1.9.0/72 paths.
O ciclo focal Alembic upgrade/downgrade/upgrade passou; PostgreSQL real fica para o
Backend CI. R-042 está mitigado parcialmente/monitorado; Package 2 não foi iniciado.

## 2026-08-06 — TASK-V19-002 planned pause

Estado `PAUSED_PLANNED_CONTINUATION_REQUIRED`. HEAD inicial `43a1907`; bloco funcional
salvo em `41ddb8b`. Foram concluídos os contratos `vena-ia.pilot-evidence/v1` e
`vena-ia.virtual-cnc-plan-validation/v1`, a composição de evidence allowlisted sem
nova persistência/migration, gate de contexto/checklist/privacy, SLO/capacity apenas
sintéticos, checksum determinístico, validação CNC `SIMULATION_ONLY` com
`executable_output=false`, auditoria existente e testes negativos G/M-code.

Testes de pausa: Ruff focal PASS; mypy focal (10 arquivos) PASS; 23 testes focais
PASS; `git diff --check` PASS. O CI vigente anterior no HEAD `43a1907` permanece
verde (Backend 31141708737, Frontend 31141708745, Runtime 31141708735); nenhum CI
novo foi disparado. Docker local continua sem daemon. Nenhum bloqueador técnico.
Próximo passo: fechar as lacunas focais registradas em `CURRENT_ORDER.md`, documentar
a matriz de evidência e somente então executar regressão/OpenAPI/CI finais.

`PLANNED_PAUSE = ACTIVE`
`CONTINUOUS_CTO_CODEX_FLOW_POLICY = TEMPORARILY_SUSPENDED`
