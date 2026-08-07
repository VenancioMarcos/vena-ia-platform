# packages/ai

Contratos, prompts e orquestração de IA da Vena_IA Platform.

Status: facade de providers reutilizada por Chat, RAG e assistência especializada.

Os perfis v2.0 Package 2 são modos bounded em
`apps/api/app/modules/engineering/assistance.py`; não são agentes autônomos e não
adicionam provider, tool calling, memória ou execução. Contratos, allowlist e limites
estão em `docs/SPECIALIZED_ASSISTANCE.md` e
`docs/GROUNDED_RESEARCH_ASSISTANCE.md`.
