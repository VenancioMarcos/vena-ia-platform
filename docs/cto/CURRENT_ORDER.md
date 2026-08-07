# Ordem CTO atual

```text
MISSION=TASK_V20_002
TITLE=V2_0_PACKAGE_2_SPECIALIZED_ASSISTANCE_AND_GROUNDED_RESEARCH
BASE=main
START_HEAD=b90bd39d9a6e14dc65a035dd2f71b0c6f95fd7ef
BRANCH=codex/v2.0-integrated-engineering-platform
EXPECTED_STATE=VENA_IA_V2_0_PACKAGE_2_READY_FOR_CTO_REVIEW
V1_9_RELEASED=TRUE
V2_0_FUNCTIONAL=PACKAGES_1_2_IMPLEMENTED_READY_FOR_CTO_REVIEW
DECISION=DEC_035_APPROVED_CTO
PACKAGE_1=APPROVED
PACKAGE_2=IMPLEMENTED_READY_FOR_CTO_REVIEW
PACKAGE_3=NOT_STARTED
FUNCTIONAL_IMPLEMENTATION=PACKAGE_2_COMPLETE
MIGRATION=PROHIBITED
DEPLOY=PROHIBITED
EXECUTABLE_CNC=PROHIBITED
TODAY_TARGET=V3_0
GOVERNANCE_BYPASS=PROHIBITED
CONTINUOUS_CTO_CODEX_FLOW_POLICY=ACTIVE
DRAFT_PR=23
BACKEND_CI=PASS_RUN_31177827093
```

Escopo executado: Package 2 adiciona assistência specialized bounded e Research
grounded sobre o snapshot determinístico aprovado. Quatro profiles allowlisted
reutilizam AIService/Documents/RAG/Research; não há sistema de agentes, provider,
persistência ou migration novos. Package 3 permanece fora. Não realizar merge da
PR funcional, deploy ou qualquer saída CNC executável.

Gate terminal: Ruff PASS; mypy 165 arquivos; pytest local 408 passed/9 skipped;
OpenAPI 77 paths; Alembic `d39a7b2c5e11`; Compose e secret scan PASS. Backend CI
run `31177827093` aprovou lint, mypy, ciclo Alembic, 341 testes API e 76 operacionais.
O gate terminal do Package 2 será registrado no fechamento desta TASK.
