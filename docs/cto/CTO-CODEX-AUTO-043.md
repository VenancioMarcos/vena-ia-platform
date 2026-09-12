# CTO-CODEX-AUTO-043 — Card de inspeção STEP

Componente declarativo `StepMetadataCard` integrado ao fluxo local de `/cam/turning`.
Exibe schema, unidade, bytes lidos e estado textual de B-Rep em um `details`
acessível; a mensagem defensiva mantém a resolução analítica profunda dependente de
despacho assíncrono. Não há controles de emissão, G-code, rede ou operação física.

## Entrega

- Commit local: `34e2e6b` (`feat(web): implement StepMetadataCard and integrate into turning viewer route`).
- Testes dedicados cobrem metadados válidos, geometria não suportada e ausência de
  controles de emissão física.
- Consolidação AUTO-044: 51 testes web, TypeScript, lint sem avisos e
  `git diff --check` aprovados.
- Parecer do CTO: **APROVADO (A)** em 2026-09-12.
- Continuidade: AUTO-044 consolida a documentação da Rota 2 Etapa 1 antes de
  qualquer autorização de sincronização remota.
